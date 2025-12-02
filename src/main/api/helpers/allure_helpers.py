import allure
import json
from functools import wraps


def allure_step(step_name: str = None):
    """
    Декоратор для автоматического создания Allure шагов
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Форматируем имя шага с параметрами
            if step_name:
                try:
                    # Пытаемся отформатировать с именованными параметрами
                    formatted_name = step_name.format(**kwargs)
                except (KeyError, IndexError):
                    try:
                        # Пытаемся с позиционными параметрами
                        formatted_name = step_name.format(*args[1:], **kwargs)
                    except:
                        formatted_name = step_name
            else:
                formatted_name = func.__name__.replace('_', ' ').capitalize()

            with allure.step(formatted_name):
                # Прикрепляем входные данные
                _attach_input_data(args, kwargs)
                # Выполняем функцию
                result = func(*args, **kwargs)
                # Прикрепляем результат
                _attach_result(result)
                return result
        return wrapper
    return decorator


def _attach_input_data(args, kwargs):
    """Прикрепить входные данные"""
    params = {}
    # Собираем все параметры (пропускаем self)
    for i, arg in enumerate(args[1:], 1):
        if hasattr(arg, '__dict__'):
            params[f'param_{i}'] = arg.__dict__
        elif not callable(arg) and not isinstance(arg, (type, object)):
            params[f'param_{i}'] = str(arg)

    for key, value in kwargs.items():
        if hasattr(value, '__dict__'):
            params[key] = value.__dict__
        elif not callable(value):
            params[key] = str(value)

    if params:
        allure.attach(
            json.dumps(params, indent=2, ensure_ascii=False, default=str),
            "📥 Request",
            allure.attachment_type.JSON
        )


def _attach_result(result):
    """Прикрепить результат"""
    if result is None:
        return
    # Если это Response объект
    if hasattr(result, 'status_code'):
        try:
            response_data = {
                "status_code": result.status_code,
                "body": result.json() if result.text else None
            }
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                f"📤 HTTP/{result.status_code}",
                allure.attachment_type.JSON
            )
        except:
            allure.attach(
                str(result),
                "📤 Response",
                allure.attachment_type.TEXT
            )
    # Если это Pydantic модель или объект с __dict__
    elif hasattr(result, '__dict__'):
        allure.attach(
            json.dumps(result.__dict__, indent=2, ensure_ascii=False, default=str),
            "📤 Response",
            allure.attachment_type.JSON
        )
