from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from data_factory import DATASET_PATH, build_dataset

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'data' / 'socialeng_model.joblib'


@dataclass
class TrainingMetrics:
    accuracy: float
    f1: float
    train_size: int
    test_size: int



def _prepare_text(df: pd.DataFrame) -> pd.Series:
    return (
        df['sender'].fillna('')
        + ' '
        + df['subject'].fillna('')
        + ' '
        + df['body'].fillna('')
    )



def train_and_save_model(
    dataset_path: Path = DATASET_PATH,
    model_path: Path = MODEL_PATH,
) -> TrainingMetrics:
    if not dataset_path.exists():
        build_dataset(dataset_path)

    df = pd.read_csv(dataset_path)
    X = _prepare_text(df)
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = Pipeline(
        [
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ('clf', LogisticRegression(max_iter=2000, random_state=42)),
        ]
    )
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    return TrainingMetrics(
        accuracy=accuracy_score(y_test, preds),
        f1=f1_score(y_test, preds),
        train_size=len(X_train),
        test_size=len(X_test),
    )



def load_or_train_model(model_path: Path = MODEL_PATH):
    if model_path.exists():
        return joblib.load(model_path)
    train_and_save_model(model_path=model_path)
    return joblib.load(model_path)


if __name__ == '__main__':
    metrics = train_and_save_model()
    print(
        f'Model trained. accuracy={metrics.accuracy:.3f}, '
        f'f1={metrics.f1:.3f}, train={metrics.train_size}, test={metrics.test_size}'
    )
