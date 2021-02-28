#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__authors__  = (
    'wrtyis@outlook.com'
 )

__license__ = 'GPLv3'
__version__ = '0.0.3'

"""
参考:
https://github.com/weizhenye/ASS/wiki/ASS-字幕格式规范


"""

""" 
鸣谢:
https://archive.org/details/youtubeannotations
https://github.com/afrmtbl/AnnotationsRestored

"""

import gettext
import argparse
import xml.etree.ElementTree
from datetime import datetime
from typing import Optional

try:
    t = gettext.translation(domain='en', localedir='locale',languages=['en_US'])
    t.install()
except:
    _ = gettext.gettext
else:
    pass

class AssTools():
    def __init__(self) -> None:
        self.info = self._info()
        self.style = self._style()
        self.event = self._event()
    class _info(object):
        def __init__(self) -> None:
            self.HEAD = "[Script Info]\n"
            self.note = "; Script generated by Annotations2Sub\n"\
                        "; https://github.com/WRTYis/Annotations2Sub\n"
            self.data={
                'Title':'Default File',
                'ScriptType':'v4.00+'}

        def add(self,k:str,v:str) -> None:
            self.data[k]=v

        def dump(self) -> str:
            data = ''
            data += self.HEAD
            data += self.note
            for k, v in self.data.items():
                data += str(k)+': '+str(v)+'\n'
            return data

    class _style(object):
        def __init__(self) -> None:
            self.HEAD = "\n"\
                        "[V4+ Styles]\n"\
                        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            self.data = {}
            self.add(Name='Default')

        def add(self,Name:str,Fontname:str='Arial',Fontsize:str=20,PrimaryColour:str='&H00FFFFFF',SecondaryColour:str='&H000000FF',OutlineColour:str='&H00000000',BackColour:str='&H00000000',Bold:int=0,Italic:int=0,Underline:int=0,StrikeOut:int=0,ScaleX:int=100,ScaleY:int=100,Spacing:int=0,Angle:int=0,BorderStyle:int=1,Outline:int=2,Shadow:int=2,Alignment:int=2,MarginL:int=10,MarginR:int=10,MarginV:int=10,Encoding:int=1) -> None:
            self.data[Name] = [Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding]

        def change(self,Name,Fontname:Optional[str]=None,Fontsize:Optional[str]=None,PrimaryColour:Optional[str]=None,SecondaryColour:Optional[str]=None,OutlineColour:Optional[str]=None,BackColour:Optional[str]=None,Bold:Optional[int]=None,Italic:Optional[int]=None,Underline:Optional[int]=None,StrikeOut:Optional[int]=None,ScaleX:Optional[int]=None,ScaleY:Optional[int]=None,Spacing:Optional[int]=None,Angle:Optional[int]=None,BorderStyle:Optional[int]=None,Outline:Optional[int]=None,Shadow:Optional[int]=None,Alignment:Optional[int]=None,MarginL:Optional[int]=None,MarginR:Optional[int]=None,MarginV:Optional[int]=None,Encoding:Optional[int]=None) -> None:
            for i,v in enumerate([Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding]):
                if v is not None:
                    self.data[Name][i] = v

        def dump(self) -> str:
            data = ''
            data += self.HEAD
            for k, v in self.data.items():
                data += 'Style: ' + str(k) +','
                for i,d in enumerate(v):
                    if i == 21:
                        data += str(d)
                    else:
                        data += str(d) + ','
                data +=  '\n'
            return data

    class _event(object):
        def __init__(self) -> None:
            self.HEAD = "\n"\
                        "[Events]\n"\
                        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            self.data = []

        def add(self,Layer:str=0, Start:str='0:00:00.00', End:str='0:00:00.00', Style:str='Default', Name:str='', MarginL:str=0, MarginR:str=0, MarginV:str=0, Effect:str='',Text:str='') -> None:
            self.data.append([Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text])

        def dump(self) -> str:
            data = ''
            data += self.HEAD
            for v in self.data:
                data += 'Dialogue: '
                for i,d in enumerate(v):
                    if i == 9:
                        data += str(d)
                    else:
                        data += str(d) + ','
                data +='\n'
            return data

class Annotations2Sub():
    def __init__(self,string:str,Title:str='默认文件') -> None:
        self.asstools = AssTools()
        self.xml = xml.etree.ElementTree.fromstring(string)
        self.asstools.info.add(k='Title',v=Title)
        self.asstools.info.add(k='PlayResX',v='100')
        self.asstools.info.add(k='PlayResY',v='100')
        self.asstools.style.change(Name='Default',Fontname='Microsoft YaHei UI')
        self._convert()
        self.asstools.event.data.sort(key=lambda x:x[1])

    def Save(self,File) -> None:
        with open(File + '.ass', 'w', encoding='utf-8') as f:
            f.write(self.asstools.info.dump())
            f.write(self.asstools.style.dump())
            f.write(self.asstools.event.dump())
            print("Save in \"{}.ass\"".format(File))

    def Close(self) -> None:
        del self

    def _convert(self) -> None:
        for each in self.xml.find('annotations').findall('annotation'):

            #提取 annotation id
            Name = each.get('id')

            #提取时间
            #h:mm:ss.ms
            _Segment = each.find('segment').find('movingRegion').findall('rectRegion')
            if _Segment is None:
                _Segment = each.find('segment').find('movingRegion').findall('anchoredRegion')
            if _Segment is None:
                Start = '0:00:00.00'
                End = '0:00:00.00'
            if _Segment is not None:
                Start =datetime.strftime(datetime.strptime(min(_Segment[0].get('t'), _Segment[1].get('t')),"%M:%S.%f"),"%H:%M:%S.%f")[:-4]
                End = datetime.strftime(datetime.strptime(max(_Segment[0].get('t'), _Segment[1].get('t')),"%M:%S.%f"),"%H:%M:%S.%f")[:-4]
            if "never" in (Start, End):
                Start = '0:00:00.00'
                End = '999:00:00.00'

            #提取样式
            style = each.get('style')

            #提取文本
            Text = each.find('TEXT')
            if Text is not  None:
                Text = Text.text.replace('\n',r'\N')
            else:
                Text = ''
            
            #提取颜色
            if each.find('appearance') == None:
                fgColor = r'&HFFFFFF&'
                bgColor = r'&H000000&'
            else:
                fgColor = r'&H'+str(hex(int(each.find('appearance').get('fgColor')))).replace('0x','').zfill(6)+r'&'
                bgColor = r'&H'+str(hex(int(each.find('appearance').get('bgColor')))).replace('0x','').zfill(6)+r'&'

            #提取文本大小
            fontsize = each.find('appearance').get('textSize')


            #提取透明度
            bgAlpha = r'&H'+str(hex(int((1-float(each.find('appearance').get('bgAlpha')))*255))).replace('0x','')+r'&'

            #处理文本框
            '''
                x,y: 文本框左上角的坐标
                w,h: 文本框的宽度和高度
            '''
            (x, y, w, h) = map(float,(_Segment[0].get(i) for i in ('x','y','w','h')))
            FullyTransparent = r'&HFF&'
            if style == 'popup':
                Name += r'_popup'
                TextBox = "m 0 0 l {0} 0 l {0} {1} l 0 {1} ".format(w,h)
                TextBox = r'{\p1}'+ TextBox +r'{\p0}'
                TextBox=self._tab_helper(Text=TextBox,PrimaryColour=bgColor,PosX=x,PosY=y,fontsize=fontsize,PrimaryAlpha=bgAlpha,SecondaryAlpha=FullyTransparent,BorderAlpha=FullyTransparent,ShadowAlpha=FullyTransparent)
                self.asstools.event.add(Start=Start,End=End,Name=Name+r'_TextBox',Text=TextBox)
                Text= self._tab_helper(Text=Text,PrimaryColour=fgColor,PosX=x,PosY=y+4,fontsize=fontsize,SecondaryAlpha=FullyTransparent,BorderAlpha=FullyTransparent,ShadowAlpha=FullyTransparent)
                self.asstools.event.add(Start=Start,End=End,Name=Name,Text=Text)
            elif style == 'title':
                Name +=r'_title'
                fontsize = str(float(fontsize)/4)
                Text= self._tab_helper(Text=Text,PrimaryColour=fgColor,PosX=x,PosY=y,fontsize=fontsize,SecondaryAlpha=FullyTransparent,BorderAlpha=FullyTransparent,ShadowAlpha=FullyTransparent)
                self.asstools.event.add(Start=Start,End=End,Name=Name,Text=Text)
            else:
                print(_("抱歉这个脚本还不能支持 {} 样式. ({})").format(style,Name))

    def _tab_helper(self,Text:Optional[str]='',PrimaryColour:Optional[str]=None,SecondaryColour:Optional[str]=None,BorderColor:Optional[str]=None,ShadowColor:Optional[str]=None,PosX:Optional[float]=None,PosY:Optional[float]=None,fontsize:Optional[str]=None,PrimaryAlpha:Optional[str]=None,SecondaryAlpha:Optional[str]=None,BorderAlpha:Optional[str]=None,ShadowAlpha:Optional[str]=None,p:Optional[str]=None) ->str:
        _tab = ''
        if (PosX,PosY) is not None:
            _pos = "\\pos({},{})".format(PosX,PosY)
            _an = r'\an7'
            _tab += _pos + _an
        if PrimaryColour is not None:
            _c = r'\c' + PrimaryColour
            _tab += _c
        if SecondaryColour is not None:
            _2c = r'\2c' + SecondaryColour
            _tab += _2c
        if BorderColor is not None:
            _3c = r'\3c' + BorderColor
            _tab += _3c
        if ShadowColor is not None:
            _4c = r'\4c' + ShadowColor
            _tab += _4c
        if fontsize is not None:
            _fs = r'\fs' + fontsize
            _tab += _fs
        if PrimaryAlpha is not None:
            _1a = r'\1a' + PrimaryAlpha
            _tab += _1a
        if SecondaryAlpha is not None:
            _2a = r'\2a' + SecondaryAlpha
            _tab += _2a
        if BorderAlpha is not None:
            _3a = r'\3a' + BorderAlpha
            _tab += _3a
        if ShadowAlpha is not None:
            _4a = r'\4a' + ShadowAlpha
            _tab += _4a
        _text = r'{' + _tab + r'}' + Text
        return _text
        #{\2c&H2425DA&\pos(208,148)}test

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=_('一个可以把Youtube注释转换成ASS字幕的脚本'))
    parser.add_argument('File',type=str,nargs='+',help=_('待转换的文件'))
    args = parser.parse_args()
    for File in args.File:
        ass = Annotations2Sub(string=open(File,'r',encoding="utf-8").read(),Title=File)
        ass.Save(File=File)
        ass.Close()
