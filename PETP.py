import logging
import platform

import wx

import utils.Logger as Logger
from mvp.model.PETPModel import PETPModel
from mvp.presenter.PETPInteractor import PETPInteractor
from mvp.presenter.PETPPresenter import PETPPresenter
from mvp.view.PETPView import PETPView
from utils.DateUtil import DateUtil
from utils.SystemConfig import SystemConfig

def init_log():
    Logger.init('petp')
    logging.info("----system starting---->>>\n"
                 + "|       " + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S") + "     |\n"
                 + "----------------------------------<<<")


def build_model():
    config = SystemConfig("/petpconfig.yaml")
    return PETPModel(config)


def build_view():
    logging.info('Init PETPView')
    return PETPView(None, wx.ID_ANY, "")


def build_presenter(model, view):
    return PETPPresenter(model, view, PETPInteractor())


def start_app():
    app = wx.App(0)

    model: PETPModel = build_model()
    view: PETPView = build_view()
    presenter: PETPPresenter = build_presenter(model, view)

    view.Show()
    logging.info('PETP is running as ' + platform.architecture()[0])

    presenter.on_load_log()

    app.MainLoop()

    logging.info('PETP is shutdown @' + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S") + '\n')


if __name__ == '__main__':
    init_log()
    start_app()
