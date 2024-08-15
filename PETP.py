import logging
import platform

import wx

import utils.Logger as Logger

from mvp.model.PETPModel import PETPModel
from mvp.presenter.PETPInteractor import PETPInteractor
from mvp.presenter.PETPPresenter import PETPPresenter
from mvp.view.PETPView import PETPView
from utils.DateUtil import DateUtil
from utils.HttpServer import HttpServer
from utils.OSUtils import OSUtils
from utils.SystemConfig import SystemConfig


def init_log():
	Logger.init('petp')
	logging.info("\n\n")
	logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
	logging.info("PETP starting @ " + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S"))


def init_display():
	OSUtils.ensure_hdpi()  # only run on windows & use autogui and canvas.


def set_log_level(m: PETPModel) -> None:
	log_level_str = getattr(m, 'log_level')
	logging.getLogger().setLevel(logging.getLevelName(log_level_str))
	getattr(logging, log_level_str.lower())('Default log level is <' + log_level_str + '>')


def build_model():
	config = SystemConfig("petpconfig.yaml")
	return PETPModel(config)


def build_view():
	logging.info('Init PETPView')
	return PETPView(None, wx.ID_ANY, "")


def build_presenter(model, view):
	return PETPPresenter(model, view, PETPInteractor())


def start_app():
	app = wx.App(False)

	model: PETPModel = build_model()
	view: PETPView = build_view()
	presenter: PETPPresenter = build_presenter(model, view)

	view.Show()

	logging.info(f'PETP is running on {platform.architecture()[0]} platform')
	set_log_level(model)

	HttpServer(presenter).start()

	presenter.on_load_log()

	app.MainLoop()

	logging.info('PETP is shutdown @' + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S"))
	logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<")


if __name__ == '__main__':
	init_log()
	init_display()
	start_app()
