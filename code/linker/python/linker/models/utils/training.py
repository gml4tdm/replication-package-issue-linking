from __future__ import annotations

import collections
import dataclasses
import json
import pathlib
import pickle
import shutil
import threading
import time
import typing

import alive_progress
import matplotlib.pyplot as pyplot
import sklearn
import torch
import torchmetrics

from .early_stopping import EarlyStopping, EarlyStoppingConfig


@dataclasses.dataclass(frozen=True)
class OptimiserConfig:
    optimiser: str | torch.optim.Optimizer
    args: dict[str, object] | None = None


@dataclasses.dataclass(frozen=True)
class LearningRateConfig:
    scheduler: str | torch.optim.lr_scheduler.LRScheduler
    args: dict[str, object] | None = None


@dataclasses.dataclass(frozen=True)
class LearningRateWarmupConfig:
    scheduler: str | type[torch.optim.lr_scheduler.LRScheduler]
    epochs_or_fraction: int | float
    args: dict[str, object] | None = None


@dataclasses.dataclass(frozen=True)
class LossConfig:
    loss: str | torch.nn.Module
    args: dict[str, object] | None = None


@dataclasses.dataclass(frozen=True)
class TrainingConfig:
    epochs: int
    loss: LossConfig
    optimiser: OptimiserConfig
    learning_rate: LearningRateConfig
    call_model_with_input_callback: typing.Callable
    task_type: typing.Literal[
        'binary-classification',
        'ranking',
        'ranking-through-binary-classification'
    ] = 'binary-classification'
    warmup: LearningRateWarmupConfig | None = None
    early_stopping: EarlyStoppingConfig | None = None
    data: DataConfig | None = None


@dataclasses.dataclass(frozen=True)
class DataConfig:
    extra_params: dict[str, int]


def _binary_fact(factory):
    return {
        'factory': factory,
        'base-args': {},
        'required-parameters': {}
    }


def _ranking_fact(factory, k):
    return {
        'factory': factory,
        'base-args': {
            'empty_target_action': 'error',
            'top_k': k,
        },
        'required-parameters': {
            'indexes': 'indexes',
        }
    }


def _ranking_fact_all(prefix, factory):
    return {
        f'{prefix}-top-1': _ranking_fact(factory, 1),
        f'{prefix}-top-3': _ranking_fact(factory, 3),
        f'{prefix}-top-5': _ranking_fact(factory, 5),
        f'{prefix}-top-10': _ranking_fact(factory, 10),
        f'{prefix}-top-20': _ranking_fact(factory, 20),
        f'{prefix}': _ranking_fact(factory, None),
    }


@dataclasses.dataclass
class ProgressUpdate:
    elapsed_time: float
    elapsed_time_since_last_report: float
    message: str


class Trainer:

    _training_lock = threading.Lock()

    _metrics = {
        'binary-classification': {
            'accuracy': _binary_fact(torchmetrics.classification.BinaryAccuracy),
            'precision': _binary_fact(torchmetrics.classification.BinaryPrecision),
            'recall': _binary_fact(torchmetrics.classification.BinaryRecall),
            'f1': _binary_fact(torchmetrics.classification.BinaryF1Score),
            'roc_auc': _binary_fact(torchmetrics.classification.BinaryAUROC),
            'confusion_matrix': _binary_fact(torchmetrics.classification.BinaryConfusionMatrix),
        },
        'ranking': {
            **_ranking_fact_all('hit-rate', torchmetrics.retrieval.RetrievalHitRate),
            **_ranking_fact_all('map', torchmetrics.retrieval.RetrievalMAP),
            **_ranking_fact_all('mrr', torchmetrics.retrieval.RetrievalMRR),
            **_ranking_fact_all('retrieval-precision', torchmetrics.retrieval.RetrievalPrecision),
            **_ranking_fact_all('retrieval-recall', torchmetrics.retrieval.RetrievalRecall),
            'r-precision': {
                'factory': torchmetrics.retrieval.RetrievalRPrecision,
                'base-args': {
                    'empty_target_action': 'error',
                },
                'required-parameters': {
                    'indexes': 'indexes',
                }
            }
        }
    }

    _metrics['ranking-through-binary-classification'] = {
        **_metrics['binary-classification'],
        **_metrics['ranking'],
    }

    def __init__(self, *,
                 config: TrainingConfig,
                 report_hook: typing.Callable[[ProgressUpdate], None],
                 is_scikit_learn_model: bool = False,
                 unpack_first_dim: bool = False,
                 generate_ranking_plots: typing.Literal['none', 'first-batch', 'all'] = 'none'):
        self._config = config
        self._progress_bar = None
        self._device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu'
        )
        self._cpu = torch.device('cpu')
        self._is_scikit_learn = is_scikit_learn_model
        self._unpack_first_dim = unpack_first_dim
        self._generate_ranking_plots = generate_ranking_plots
        if report_hook is None:
            self._report_hook = lambda x: None
        else:
            self._report_hook = report_hook
        self._start_time = None
        self._dt = None

    def train_and_eval(self,
                       model, train, validation, test, *,
                       checkpoint_dir: pathlib.Path | None = None):
        if not self._training_lock.acquire(blocking=False):
            raise RuntimeError('Trainer is already running')
        self._start_time = self._dt = time.time()
        try:
            if self._is_scikit_learn:
                return self._train_and_eval_sklearn(model,
                                                    train,
                                                    validation,
                                                    test,
                                                    checkpoint_dir)
            return self._train_and_eval(model,
                                        train,
                                        validation,
                                        test,
                                        checkpoint_dir)
        finally:
            self._training_lock.release()

    def _build_loss(self):
        conf = self._config.loss

        if isinstance(conf.loss, str):
            factory = getattr(torch.nn, conf.loss)
            if 'reduction' not in conf.args:
                raise ValueError(
                    f'`reduction` argument should be be specified for {conf.loss}'
                )
            return factory(**conf.args)
        else:
            if conf.args:
                raise ValueError(
                    f'No arguments should be specified if a loss instance is provided'
                )
            return conf.loss

    def _build_optimiser(self, model):
        conf = self._config.optimiser
        if isinstance(conf.optimiser, str):
            factory = getattr(torch.optim, conf.optimiser)
            optimiser = factory(model.parameters(), **conf.args)
        else:
            if conf.args:
                raise ValueError(
                    f'No arguments should be specified if an optimiser instance is provided'
                )
            optimiser = conf.optimiser
        scheduler = self._build_learning_rate_scheduler(optimiser)
        return optimiser, scheduler

    def _build_learning_rate_scheduler(self, optimiser):
        conf = self._config.learning_rate
        if isinstance(conf.scheduler, str):
            factory = getattr(torch.optim.lr_scheduler, conf.scheduler)
            scheduler = factory(optimiser, **conf.args)
        else:
            if conf.args:
                raise ValueError(
                    'No arguments should be specified is a lr-scheduler instance is provided'
                )
            scheduler = conf.scheduler
        if self._config.warmup is not None:
            warmup_conf = self._config.warmup
            if isinstance(warmup_conf.scheduler, str):
                factory = getattr(torch.optim.lr_scheduler, warmup_conf.scheduler)
                warmup_scheduler = factory(optimiser, **warmup_conf.args)
            else:
                if warmup_conf.args:
                    raise ValueError(
                        'No arguments should be specified if a warmup scheduler instance is provided'
                    )
                warmup_scheduler = warmup_conf.scheduler
            if isinstance(warmup_conf.epochs_or_fraction, int):
                epochs = warmup_conf.epochs_or_fraction
            else:
                epochs = int(warmup_conf.epochs_or_fraction * self._config.epochs)
            return torch.optim.lr_scheduler.SequentialLR(
                optimiser,
                schedulers=[warmup_scheduler, scheduler],
                milestones=[epochs],
            )
        return scheduler

    def _build_early_stopping(self):
        conf = self._config.early_stopping
        if conf is None:
            return None
        return EarlyStopping(conf)

    def _train_and_eval(self, model, train, validation, test, checkpoint_dir):
        total_steps = self._calculate_total_duration(train, validation, test)
        plot_dir = checkpoint_dir / 'plots'
        loss_fn = self._build_loss()
        optimiser, scheduler = self._build_optimiser(model)
        early_stopping = self._build_early_stopping()
        final_key = 'evaluation'
        result = {'train': [], 'validation': [], 'test': []}
        model = model.to(self._device)
        with alive_progress.alive_bar(total_steps) as self._progress_bar:
            for epoch in range(1, self._config.epochs + 1):
                model.train(True)
                _loss = self._train_epoch(model, train, optimiser, loss_fn, epoch)
                #result['train'].append({'loss': loss})
                report= self._evaluate(model, train, loss_fn, epoch, 'train (eval)', plot_dir)
                result['train'].append(report)

                scheduler.step()
                model.eval()
                report = self._evaluate(model, validation, loss_fn, epoch, 'validation', plot_dir)
                val_loss = report['loss']
                stop_early = False
                if early_stopping is not None:
                    if early_stopping.early_stop(val_loss):
                        final_key = f'evaluation [stopped early @ E:{epoch}]'
                        stop_early = True
                result['validation'].append(report)
                report = self._evaluate(model, test, loss_fn, epoch, final_key, plot_dir)
                result['test'].append(report)
                self._store_checkpoint(epoch, model, result, checkpoint_dir)
                if stop_early:
                    break
        self._store_checkpoint('final', model, result, checkpoint_dir)
        return result

    def _train_epoch(self, model, loader, optimiser, loss_fn, epoch):
        if self._config.data is None:
            extra_params = {}
        else:
            extra_params = self._config.data.extra_params
        running_loss = 0.0
        batch_max = len(loader)
        for i_batch, data in enumerate(loader, start=1):
            if self._unpack_first_dim:
                data = self._unpack_batch(data)
            self._report(
                f'Training E:{epoch} B:{i_batch}/{batch_max} '
                f'-- {running_loss / i_batch:.5f}'
            )
            if not data:
                continue
            inputs, targets, *extra = data
            extra_map = {k: extra[v] for k, v in extra_params.items()}
            optimiser.zero_grad()
            _outputs, loss, _new_targets, _new_extra = self._config.call_model_with_input_callback(
                model, inputs, targets, loss_fn, self._device, 'train', i_batch, extra_map
            )
            loss.backward()
            optimiser.step()
            running_loss += loss.item()
        return running_loss / batch_max

    def _evaluate(self, model, loader, loss_fn, epoch, which, plots_directory: pathlib.Path):
        running_loss = 0.0
        batch_max = len(loader)
        if self._config.data is None:
            extra_params = {}
        else:
            extra_params = self._config.data.extra_params
        with torch.no_grad():
            aggregated_targets = []
            aggregated_outputs = []
            aggregated_extra = collections.defaultdict(list)
            for i_batch, data in enumerate(loader, start=1):
                if self._unpack_first_dim:
                    data = self._unpack_batch(data)
                self._report(
                    f'{which.capitalize()} E:{epoch} B:{i_batch}/{batch_max} '
                    f'-- {running_loss / i_batch:.5f}'
                )
                if not data:
                    continue
                inputs, targets, *extra = data
                extra_map = {k: extra[v] for k, v in extra_params.items()}
                outputs, loss, new_targets, new_extra = self._config.call_model_with_input_callback(
                    model, inputs, targets, loss_fn, self._device, 'pred', i_batch, extra_map
                )
                if new_targets is not None:
                    targets = new_targets
                if new_extra is not None:
                    extra_map = new_extra
                aggregated_targets.append(targets)
                aggregated_outputs.append(outputs)
                for k, v in extra_map.items():
                    aggregated_extra[k].append(v)
                running_loss += loss.item()
            all_targets = torch.cat(aggregated_targets)
            all_outputs = torch.cat(aggregated_outputs)
            all_extra = {k: torch.cat(v) for k, v in aggregated_extra.items()}
            out = self.evaluate(all_outputs,
                                all_targets,
                                self._config.task_type,
                                **all_extra)
            out['loss'] = running_loss / batch_max
            if self._config.task_type in ('ranking', 'ranking-through-binary-classification'):
                if self._generate_ranking_plots != 'none':
                    self.plot_ranking(all_outputs,
                                      all_targets,
                                      self._config.task_type,
                                      directory=plots_directory / f'E{epoch}/{which}',
                                      filename_base='plt',
                                      first_group_only=self._generate_ranking_plots == 'first-batch',
                                      **all_extra)
        return out

    def _train_and_eval_sklearn(self,  model, train, validation, test, checkpoint_dir):
        # This is just a watered down version of the Torch training code.
        total_steps = self._calculate_total_duration(train, validation, test)
        final_key = 'Evaluation'
        result = {'train': [], 'validation': [], 'test': []}

        def _train_func(m, x, y):
            m.partial_fit(x, y, classes=[False, True])
            return m.predict_proba(x)[:, 1]

        with alive_progress.alive_bar(total_steps) as self._progress_bar:
            for epoch in range(1, self._config.epochs + 1):
                # Training
                loss, _ = self._sklearn_epoch(
                    model, _train_func, train, epoch, 'Training'
                )
                result['train'].append({'loss': loss})

                # Validation
                _, pred = self._sklearn_epoch(
                    model,
                    lambda m, x, y: m.predict_proba(x)[:, 1],
                    validation,
                    epoch,
                    'Validation',
                    return_pred=True
                )
                predictions, targets, extras = pred
                report = self.evaluate(predictions, targets, self._config.task_type, **extras)
                result['validation'].append(report)
                self._store_checkpoint(epoch, model, result, checkpoint_dir)
                _, pred = self._sklearn_epoch(
                    model,
                    lambda m, x, y: m.predict_proba(x)[:, 1],
                    validation,
                    epoch,
                    final_key,
                    return_pred=True
                )
                predictions, targets, extras = pred
                report = self.evaluate(predictions, targets, self._config.task_type, **extras)
                result['test'].append(report)
        self._store_checkpoint('final', model, result, checkpoint_dir)
        return result

    @torch.no_grad()
    def _sklearn_epoch(self, model, cb, loader, epoch, prefix, *, return_pred=False):
        running_loss = 0.0
        batch_max = len(loader)
        extras = collections.defaultdict(list)
        predictions = []
        all_targets = []
        if self._config.data is None:
            extra_params = {}
        else:
            extra_params = self._config.data.extra_params
        for i_batch, data in enumerate(loader, start=1):
            self._report(
                f'{prefix} E:{epoch} B:{i_batch}/{batch_max} '
                f'-- {running_loss / i_batch:.5f}'
            )
            inputs, targets, *extra = data
            np_targets = targets.numpy()
            pred = cb(model, inputs, np_targets)
            loss = sklearn.metrics.log_loss(np_targets, pred, labels=[False, True])
            running_loss += loss
            if return_pred:
                predictions.append(torch.from_numpy(pred))
                all_targets.append(targets)
                for k, v in extra_params.items():
                    extras[k].append(extra[v])
        pred_out = None
        if return_pred:
            pred_out = (
                torch.cat(predictions),
                torch.cat(all_targets),
                {k: torch.cat(v) for k, v in extras.items()}
            )
        return running_loss / batch_max, pred_out

    @classmethod
    def evaluate(cls, predictions, targets, task, **extra):
        metrics_blueprint = cls._metrics[task]
        metrics = {
            k: (v['factory'](**v['base-args']), v['required-parameters'])
            for k, v in metrics_blueprint.items()
        }
        out = {}
        with torch.no_grad():
            for name, (metric, required) in metrics.items():
                selected_extra = {r: extra[r] for r in required}
                value = metric(predictions, targets, **selected_extra)
                try:
                    value = value.item()
                except RuntimeError:
                    value = value.tolist()
                out[name] = value
                metric.reset()
        return out

    @classmethod
    def evaluate_numpy(cls, predictions, targets, task, **extra):
        extra = {k: torch.from_numpy(v) for k, v in extra.items()}
        return cls.evaluate(torch.from_numpy(predictions),
                            torch.from_numpy(targets),
                            task,
                            **extra)

    @classmethod
    def evaluate_std(cls, predictions, targets, task, **extra):
        extra = {k: torch.tensor(v) for k, v in extra.items()}
        return cls.evaluate(torch.tensor(predictions),
                            torch.tensor(targets),
                            task,
                            **extra)

    @classmethod
    def plot_ranking(cls,
                     predictions,
                     targets,
                     task, *,
                     directory: pathlib.Path,
                     filename_base: str,
                     first_group_only: bool = False,
                     group_size=40,
                     noise=0.25,
                     **extra):
        if task not in ('ranking', 'ranking-through-binary-classification'):
            raise ValueError(f'Task {task} is not supported for plotting')
        indexes = extra['indexes']
        groups = torch.unique(indexes)
        directory.mkdir(parents=True, exist_ok=True)
        for g, batch in enumerate(groups.split(group_size), start=1):
            px = 1 / pyplot.rcParams['figure.dpi']
            fig, ax = pyplot.subplots(
                figsize=(1920 * px, 900 * px)
            )
            positives = targets == True
            negatives = targets == False

            x, y = cls._prepare_for_ax(batch, predictions[negatives], indexes[negatives], noise)
            ax.scatter(x, y, label='Negative')

            x, y = cls._prepare_for_ax(batch, predictions[positives], indexes[positives], noise)
            ax.scatter(x, y, label='Positive')


            ax.legend()
            ax.set_title(f'Group {g}')
            pyplot.tight_layout()
            pyplot.savefig(directory / f'{filename_base}-{g}.png')
            pyplot.close(fig)

            if first_group_only:
                break

    @staticmethod
    def _prepare_for_ax(batch, predictions, indexes, noise):
        mapping = {x.item(): i for i, x in enumerate(batch)}
        x = []
        y = []
        for index, pred in zip(indexes, predictions, strict=True):
            index = index.item()
            if index not in mapping:
                continue
            x.append(mapping[index])
            y.append(pred.item())
        x = torch.tensor(x)
        y = torch.tensor(y)
        scatter = (torch.rand(len(y)) - 0.5) * noise
        return x + scatter, y

    def _report(self, message: str):
        assert self._progress_bar is not None
        assert self._start_time is not None
        assert self._dt is not None
        assert self._report_hook is not None
        self._progress_bar.title(message)
        self._progress_bar()
        dt = time.time()
        progress = ProgressUpdate(
            elapsed_time=dt - self._start_time,
            elapsed_time_since_last_report=dt - self._dt,
            message=message
        )
        self._report_hook(progress)
        self._dt = dt


    def _calculate_total_duration(self, train, validation, test):
        total = 0
        total += len(train) * self._config.epochs
        total += len(validation) * self._config.epochs
        total += len(test)
        return total

    def _store_checkpoint(self, epoch: int | str, model, result, loc: pathlib.Path):
        if loc is None:
            return
        directory = loc / f'E{epoch}'
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / 'performance.json', 'w') as f:    # type: ignore
            json.dump(result, f, indent=2)                      # type: ignore
        if self._is_scikit_learn:
            with open(directory / 'model.pkl', 'wb') as f:      # type: ignore
                pickle.dump(model, f)                           # type: ignore
        else:
            torch.save(model, directory / 'model.pt')

        if isinstance(epoch, int) or (isinstance(epoch, str) and epoch.isdigit()):
            epoch = int(epoch)
            old_dir = loc / f'E{epoch - 1}'
            if old_dir.exists():
                shutil.rmtree(old_dir)

    def _unpack_batch(self, batch):
        if isinstance(batch, dict):
            return {
                k: self._unpack_batch(v)
                for k, v in batch.items()
            }
        elif isinstance(batch, tuple):
            return tuple(self._unpack_batch(v) for v in batch)
        elif isinstance(batch, list):
            return [self._unpack_batch(v) for v in batch]
        elif isinstance(batch, torch.Tensor):
            assert batch.shape[0] == 1
            return batch[0]
        else:
            return batch

