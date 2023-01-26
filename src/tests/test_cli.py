#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.request

import pytest

from Annotations2Sub import cli
from Annotations2Sub.cli import run
from Annotations2Sub.utils import RedText, Stderr

path = os.path.dirname(__file__)
file1 = os.path.join(path, "Baseline", "29-q7YnyUmY.xml.test")
file2 = os.path.join(path, "Baseline", "e8kKeUuytqA.xml.test")
file3 = os.path.join(path, "test", "1.xml.test")
file4 = os.path.join(path, "test", "2.xml.test")
file5 = os.path.join(path, "test", "1.ass.test")


def test_cli():
    test = f"""-s {file1} -o {file5}
-s {file1} -O {file5}
-s {file1} -D
-s {file1} -p
-s {file1} -g
-N -D {file1}
{file1} -o {file5}
0
-d 0
{file3}
{file5}
{file1} {file2} -O 1.ass
{file1} -o . -O 1.ass"""
    for line in test.splitlines():
        argv = line.split(" ")
        code = run(argv)
        if code != 1:
            Stderr(RedText(line))
        assert code == 1


def test_cli2():
    test = f"""{file1} {file2} -l -x 1920 -y 1080 -f Microsoft -V -o .
{file1} -l
{file1} -O 1.ass
{file1} -s
{file4}
{file1} -n
"""
    for line in test.splitlines():
        argv = line.split(" ")
        code = run(argv)
        assert code == 0


def test_cli3():
    m = pytest.MonkeyPatch()
    m.setattr(cli, "urllibWapper", lambda __: "")

    code = run(["-d", "00000000000"])
    assert code == 1


def test_cli4():
    with open(file1, encoding="utf-8") as f:
        s = f.read()
    m = pytest.MonkeyPatch()
    m.setattr(cli, "urllibWapper", lambda __: s)

    code = run(["-d", "29-q7YnyUmY", "-N", "-n"])
    assert code == 0

    code = run(["-D", "29-q7YnyUmY"])
    assert code == 0


def test_cli5():
    t1 = "29-q7YnyUmY"
    t = f"""-pN {t1}
-g {t1}
-gn {t1}
-g {t1} -o .
-D {t1} -O 1.xml"""

    s1 = r'{"adaptiveFormats":[{"type":"video","bitrate":1,"url":"1"},{"type":"audio","bitrate":1,"url":"2"}]}'
    s2 = r'[["1"],["2"]]'
    with open(file1, encoding="utf-8") as f:
        s3 = f.read()

    def mock(url: str):
        if (
            url
            == "https://archive.org/download/youtubeannotations_54/29.tar/29-/29-q7YnyUmY.xml"
        ):
            return s3
        if url == "https://api.invidious.io/instances.json":
            return s2
        if url == "https://1/api/v1/videos/29-q7YnyUmY":
            return ""
        if url == "https://2/api/v1/videos/29-q7YnyUmY":
            return s1

        raise Exception

    m = pytest.MonkeyPatch()
    m.setattr(cli, "urllibWapper", mock)
    m.setattr(os, "system", lambda __: None)

    for line in t.splitlines():
        argv = line.split(" ")
        code = run(argv)
        assert code == 0

    with pytest.raises(Exception):
        mock("")


def test_cli6():
    def a(a1):
        for i in a1:
            if i.__name__ == "CheckUrl":
                i()

    def b(*args, **kwargs):
        return

    def c(*args, **kwargs):
        raise Exception

    m = pytest.MonkeyPatch()
    m.setattr(cli, "Dummy", a)
    m.setattr(urllib.request, "urlopen", b)
    with pytest.raises(SystemExit):
        run([])
    m.setattr(urllib.request, "urlopen", c)
    with pytest.raises(SystemExit):
        run([])


def test_cli7():
    pass
