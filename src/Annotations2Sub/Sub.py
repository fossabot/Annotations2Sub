#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
https://github.com/weizhenye/ASS/wiki/ASS-字幕格式规范
"""

import datetime
from typing import Dict, List, Literal

from Annotations2Sub.Color import Alpha, Color, Rgba


class Style:
    def __init__(self):
        self.Fontname: str = "Arial"
        self.Fontsize: float = 20
        self.PrimaryColour: Rgba = Rgba(Color(255, 255, 255), Alpha(0))
        self.SecondaryColour: Rgba = Rgba(Color(255, 0, 0), Alpha(0))
        self.OutlineColour: Rgba = Rgba(Color(0, 0, 0), Alpha(0))
        self.BackColour: Rgba = Rgba(Color(0, 0, 0), Alpha(0))
        self.Bold: Literal[-1, 0] = 0
        self.Italic: Literal[-1, 0] = 0
        self.Underline: Literal[-1, 0] = 0
        self.StrikeOut: Literal[-1, 0] = 0
        self.ScaleX: int = 100
        self.ScaleY: int = 100
        self.Spacing: int = 0
        self.Angle: float = 0
        self.BorderStyle: Literal[1, 3] = 1
        self.Outline: Literal[0, 1, 2, 3, 4] = 2
        self.Shadow: Literal[0, 1, 2, 3, 4] = 2
        self.Alignment: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] = 2
        self.MarginL: int = 10
        self.MarginR: int = 10
        self.MarginV: int = 10
        self.Encoding: int = 1


class Event:
    """Sub 的 Event 结构"""

    def __init__(self):

        # 仅列出了需要的 Format
        self.Format: Literal["Dialogue"] = "Dialogue"
        # Aegisub 没有 Marked ,所以我们也没有
        self.Layer: int = 0
        self.Start: datetime.datetime = datetime.datetime()
        self.End: datetime.datetime = datetime.datetime()
        self.Style: str = "Default"
        self.Name: str = ""
        # MarginL, MarginR, MarginV, Effect 在本项目中均没有使用
        self.MarginL: int = 0
        self.MarginR: int = 0
        self.MarginV: int = 0
        self.Effect: str = ""
        self.Text: str = ""


class Point:
    """绘图命令"""

    def __init__(self, x=0, y=0, command="m"):
        self.x: int = x
        self.y: int = y
        # 仅列出需要的命令
        self.command: Literal["m", "l"] = command


class Draw:
    def __init__(self):
        self.draw: List[Point] = []

    def Add(self, point: Point):
        self.draw.append(point)

    def Dump(self) -> str:
        s = ""
        for i in self.draw:
            s = s + "{} {} {} ".format(i.command, i.x, i.y)
        return s


class Sub:
    def __init__(self):
        self.info = self.Info()
        self.styles = self.Styles()
        self.events = self.Events()

        self.note.info["Title"] = "Default File"
        self.info.note = (
            "; Script generated by Annotations2Sub" + "\n"
            "; https://github.com/WRTYis/Annotations2Sub" + "\n"
        )
        self.styles.styles["Default"] = Style()

    class Info:
        def __init__(self):
            self.note = ""
            self.info = {"ScriptType": "v4.00+"}

        def Dump(self) -> str:
            s = ""
            s += "[Script Info]" + "\n"
            s += self.note
            for k, v in self.info.items():
                s += "{}:{}\n".format(k, v)
            s += "\n"
            return s

    class Styles:
        def __init__(self):
            self.styles: Dict[str, Style] = {}

        def Dump(self) -> str:
            def ConvertRgbaToAABBGGRR(rgba: Rgba) -> str:
                return "&H{:02X}{:02X}{:02X}{:02X}".format(
                    rgba.alpha.alpha, rgba.color.blue, rgba.color.green, rgba.color.red
                )

            s = ""
            s += "[V4+ Styles]" + "\n"
            s += (
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
                + "\n"
            )
            for name, each in self.styles.items():
                s += "Style: "
                s += name + ","
                s += each.Fontname + ","
                s += str(each.Fontsize) + ","
                s += ConvertRgbaToAABBGGRR(each.PrimaryColour) + ","
                s += ConvertRgbaToAABBGGRR(each.SecondaryColour) + ","
                s += ConvertRgbaToAABBGGRR(each.OutlineColour) + ","
                s += ConvertRgbaToAABBGGRR(each.BackColour) + ","
                s += str(each.Bold) + ","
                s += str(each.Italic) + ","
                s += str(each.Underline) + ","
                s += str(each.StrikeOut) + ","
                s += str(each.ScaleX) + ","
                s += str(each.ScaleY) + ","
                s += str(each.Spacing) + ","
                s += str(each.Angle) + ","
                s += str(each.BorderStyle) + ","
                s += str(each.Outline) + ","
                s += str(each.Shadow) + ","
                s += str(each.Alignment) + ","
                s += str(each.MarginL) + ","
                s += str(each.MarginR) + ","
                s += str(each.MarginV) + ","
                s += str(each.Encoding) + "\n"
            s += "\n"
            return s

    class Events:
        def __init__(self):
            self.events: List[Event] = []

        def Dump(self) -> str:
            def ConvertTime(t: datetime.datetime) -> str:
                return t.strftime("%H:%M:%S.%f")

            s = ""
            s += "[Events]" + "\n"
            s += (
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
                + "\n"
            )
            for each in self.events:
                s += "Dialogue: "
                s += str(each.Layer) + ","
                s += ConvertTime(each.Start) + ","
                s += ConvertTime(each.End) + ","
                s += each.Style + ","
                s += each.Name + ","
                s += str(each.MarginL) + ","
                s += str(each.MarginR) + ","
                s += str(each.MarginV) + ","
                s += each.Effect + ","
                s += each.Text + "\n"
            s += "\n"
            return s

    def Dump(self) -> str:
        s = ""
        s += self.info.Dump()
        s += self.styles.Dump()
        s += self.events.Dump()
        return s
