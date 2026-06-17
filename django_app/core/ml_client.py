"""Client wrapper around the FastAPI ML service."""
from __future__ import annotations

import requests
from django.conf import settings


class MLServiceError(Exception):
    pass


def _base_url() -> str:
    return settings.FASTAPI_URL.rstrip('/')


def predict(payload: dict, timeout: int = 30) -> dict:
    try:
        resp = requests.post(f'{_base_url()}/predict', json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise MLServiceError(f'Could not reach the ML service: {exc}') from exc
    if resp.status_code != 200:
        raise MLServiceError(_detail(resp))
    return resp.json()


def predict_bulk(payloads: list[dict], timeout: int = 120) -> list[dict]:
    try:
        resp = requests.post(
            f'{_base_url()}/predict-bulk', json=payloads, timeout=timeout
        )
    except requests.RequestException as exc:
        raise MLServiceError(f'Could not reach the ML service: {exc}') from exc
    if resp.status_code != 200:
        raise MLServiceError(_detail(resp))
    return resp.json()


def feature_importance(timeout: int = 15) -> list[dict]:
    try:
        resp = requests.get(f'{_base_url()}/feature-importance', timeout=timeout)
    except requests.RequestException as exc:
        raise MLServiceError(f'Could not reach the ML service: {exc}') from exc
    if resp.status_code != 200:
        raise MLServiceError(_detail(resp))
    return resp.json()


def retrain_model(rows: list[dict], use_synthetic: bool = False, synthetic_n: int = 3000, timeout: int = 300) -> dict:
    payload = {
        'rows': rows,
        'use_synthetic': use_synthetic,
        'synthetic_n': synthetic_n,
    }
    try:
        resp = requests.post(
            f'{_base_url()}/train', json=payload, timeout=timeout
        )
    except requests.RequestException as exc:
        raise MLServiceError(f'Could not reach the ML service: {exc}') from exc
    if resp.status_code != 200:
        raise MLServiceError(_detail(resp))
    return resp.json()


def _detail(resp: requests.Response) -> str:
    try:
        return resp.json().get('detail', resp.text)
    except ValueError:
        return resp.text or f'ML service returned status {resp.status_code}'
