"""V5 強型別輸出 schema — Pydantic + OpenAI JSON Schema strict mode

設計目標：
  - 用 Pydantic 寫死 11 個欄位的型別 + 可空性
  - 透過 model_json_schema(by_alias=True) 自動 export 給 OpenAI 用
  - OpenAI structured outputs (strict=true) 強制 LLM 回傳合法 JSON
    - 不能漏欄位（all required）
    - 不能多欄位（additionalProperties: false）
    - 型別跑掉直接 reject 而不是 LLM 自己編

欄位名一字不漏對齊 specbook.xlsx：
  - "Minimum Operating Temperature(°C)"  ← ( 前無空白
  - "Maximum Operating Temperature (°C)" ← ( 前有 1 個空白
  - "I_O、I_F (A)"                       ← 全形頓號
  - "I_R(Reverse Current) "              ← 尾端有 1 個空白

OpenAI strict mode 限制：
  - 必填欄位用 Union[T, None] 而非 Optional[T] 才能正確 type=["X","null"]
  - additionalProperties 必須 false
  - 所有 properties 必須在 required 內（即使可 null）
"""
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ComponentData(BaseModel):
    """電子元件 datasheet 抽取的標準化 schema（11 欄位）。

    用 alias 對齊 specbook.xlsx 的中文 / 特殊字元欄位名。
    Union[T, None] 是讓 OpenAI strict mode 接受 nullable 欄位。
    """
    model_config = ConfigDict(populate_by_name=True)

    part_number: str = Field(alias="Part Number")
    min_temp_c: Union[int, None] = Field(alias="Minimum Operating Temperature(°C)", default=None)
    max_temp_c: Union[int, None] = Field(alias="Maximum Operating Temperature (°C)", default=None)
    max_length_mm: Union[float, None] = Field(alias="Maximum Length (mm)", default=None)
    max_width_mm: Union[float, None] = Field(alias="Maximum Width (mm)", default=None)
    max_height_mm: Union[float, None] = Field(alias="Maximum Height (mm)", default=None)
    pin_number: Union[int, None] = Field(alias="PIN Number", default=None)
    io_if_a: Union[float, None] = Field(alias="I_O、I_F (A)", default=None)
    v_f_v: Union[str, None] = Field(alias="V_F(Forward Voltage) (V)", default=None)
    v_rrm_v: Union[int, None] = Field(alias="V_RRM(Peak Repetitive Reverse Voltage) (V)", default=None)
    i_r: Union[str, None] = Field(alias="I_R(Reverse Current) ", default=None)


def _build_openai_strict_schema() -> dict:
    """把 Pydantic schema 轉成 OpenAI json_schema strict 格式。

    OpenAI 要求：
      - top-level "name" 必填（任意字串 id）
      - "strict": true
      - "schema" 內所有 properties 必須在 required 內
      - "additionalProperties": false
    """
    pyd_schema = ComponentData.model_json_schema(by_alias=True)
    properties = pyd_schema.get("properties", {})

    # OpenAI strict 要求：所有 property 都 required（用 union with null 表達 nullable）
    all_props = list(properties.keys())

    return {
        "type": "json_schema",
        "json_schema": {
            "name": "ComponentData",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": properties,
                "required": all_props,
                "additionalProperties": False,
            },
        },
    }


# 預先 build 好，給 backend 直接用
OPENAI_RESPONSE_FORMAT_STRICT = _build_openai_strict_schema()


# 給 main.py 用：從 LLM raw response 解析成 dict（保持原欄位 alias 名）
def parse_response(raw_json_str: str) -> dict:
    """用 Pydantic 解析 LLM 回應字串，回傳 dict (用 alias 命名，跟 specbook 對齊)"""
    import json
    parsed_dict = json.loads(raw_json_str)
    model = ComponentData.model_validate(parsed_dict)
    return model.model_dump(by_alias=True)
