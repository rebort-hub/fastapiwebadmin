# -*- coding: utf-8 -*-
"""验证码生成。"""

import base64
import random
import string
import uuid


class CaptchaUtil:
    CAPTCHA_WIDTH = 132
    CAPTCHA_HEIGHT = 40

    @staticmethod
    def _svg_to_data_uri(svg: str) -> str:
        encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{encoded}"

    @classmethod
    def _build_svg(cls, text: str, *, font_size: int | None = None) -> str:
        width, height = cls.CAPTCHA_WIDTH, cls.CAPTCHA_HEIGHT
        size = font_size or max(18, min(30, int(width / max(len(text), 1) * 1.45)))
        noise = "".join(
            f'<line x1="{random.randint(0, width)}" y1="{random.randint(0, height)}" '
            f'x2="{random.randint(0, width)}" y2="{random.randint(0, height)}" '
            f'stroke="rgb({random.randint(180, 220)},{random.randint(180, 220)},{random.randint(190, 230)})" '
            f'stroke-width="1" opacity="0.8"/>'
            for _ in range(4)
        )
        dots = "".join(
            f'<circle cx="{random.randint(0, width)}" cy="{random.randint(0, height)}" r="1" '
            f'fill="rgb({random.randint(120, 180)},{random.randint(120, 180)},{random.randint(120, 180)})" opacity="0.5"/>'
            for _ in range(10)
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" preserveAspectRatio="none">'
            f'<rect width="{width}" height="{height}" fill="#f8fafc"/>'
            f"{noise}{dots}"
            f'<text x="{width / 2}" y="{height / 2 + size * 0.18}" text-anchor="middle" '
            f'font-size="{size}" font-family="Arial,Helvetica,sans-serif" '
            f'fill="#1f2937" font-weight="700" letter-spacing="0.5">{text}</text>'
            f"</svg>"
        )

    @classmethod
    def generate_text_captcha(cls) -> tuple[str, str, str]:
        """生成字符验证码，返回 key、data-uri 图片、答案。"""
        captcha_key = uuid.uuid4().hex
        chars = string.digits + string.ascii_uppercase
        answer = "".join(random.choices(chars, k=4))
        svg = cls._build_svg(answer, font_size=28)
        return captcha_key, cls._svg_to_data_uri(svg), answer

    @classmethod
    def generate_arithmetic_captcha(cls) -> tuple[str, str, int]:
        """生成算术验证码，返回 key、data-uri 图片、答案。"""
        captcha_key = uuid.uuid4().hex
        operator = random.choice(["+", "-", "*"])
        if operator == "-":
            left = random.randint(5, 20)
            right = random.randint(1, left - 1)
            answer = left - right
        elif operator == "*":
            left = random.randint(2, 9)
            right = random.randint(2, 9)
            answer = left * right
        else:
            left = random.randint(1, 20)
            right = random.randint(1, 20)
            answer = left + right
        text = f"{left} {operator} {right} = ?"
        svg = cls._build_svg(text)
        return captcha_key, cls._svg_to_data_uri(svg), answer
