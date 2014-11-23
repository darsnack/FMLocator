#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Stereo FM receiver and RDS Decoder
# Generated: Sun Nov 23 12:38:00 2014
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import digital;import cmath
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import scopesink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import osmosdr
import rds
import wx

class rds_rx(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Stereo FM receiver and RDS Decoder")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.bb_decim = bb_decim = 4
        self.freq_offset = freq_offset = 250000
        self.freq = freq = 101.5
        self.baseband_rate = baseband_rate = samp_rate/bb_decim
        self.audio_decim = audio_decim = 5
        self.xlate_bandwidth = xlate_bandwidth = 100000
        self.gain = gain = 20
        self.freq_tune = freq_tune = freq - freq_offset
        self.audio_rate = audio_rate = 48000
        self.audio_decim_rate = audio_decim_rate = baseband_rate/audio_decim

        ##################################################
        # Blocks
        ##################################################
        self.nb = self.nb = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "BB")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Demod")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "L+R")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Pilot")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "DSBSC")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "RDS")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "L-R")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "RDS constellation")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Waterfall")
        self.GridAdd(self.nb, 2, 0, 1, 2)
        self.wxgui_scopesink2_1 = scopesink2.scope_sink_c(
        	self.nb.GetPage(7).GetWin(),
        	title="Scope Plot",
        	sample_rate=2375,
        	v_scale=0.4,
        	v_offset=0,
        	t_scale=0,
        	ac_couple=False,
        	xy_mode=True,
        	num_inputs=1,
        	trig_mode=wxgui.TRIG_MODE_AUTO,
        	y_axis_label="Counts",
        )
        self.nb.GetPage(7).Add(self.wxgui_scopesink2_1.win)
        self.wxgui_fftsink2_0_0_0_1_0_1 = fftsink2.fft_sink_c(
        	self.nb.GetPage(5).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=audio_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="RDS",
        	peak_hold=False,
        )
        self.nb.GetPage(5).Add(self.wxgui_fftsink2_0_0_0_1_0_1.win)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.nb.GetPage(0).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=-30,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.8,
        	title="Baseband",
        	peak_hold=False,
        )
        self.nb.GetPage(0).Add(self.wxgui_fftsink2_0.win)
        self.rtl_sdr_source0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.rtl_sdr_source0.set_sample_rate(samp_rate)
        self.rtl_sdr_source0.set_center_freq(freq_tune, 0)
        self.rtl_sdr_source0.set_freq_corr(0, 0)
        self.rtl_sdr_source0.set_dc_offset_mode(0, 0)
        self.rtl_sdr_source0.set_iq_balance_mode(0, 0)
        self.rtl_sdr_source0.set_gain_mode(False, 0)
        self.rtl_sdr_source0.set_gain(gain, 0)
        self.rtl_sdr_source0.set_if_gain(20, 0)
        self.rtl_sdr_source0.set_bb_gain(20, 0)
        self.rtl_sdr_source0.set_antenna("", 0)
        self.rtl_sdr_source0.set_bandwidth(0, 0)
          
        self.root_raised_cosine_filter_0 = filter.fir_filter_ccf(1, firdes.root_raised_cosine(
        	1, samp_rate/bb_decim/audio_decim, 2375, 1, 100))
        self.gr_rds_parser_0 = rds.parser(True, False)
        self.gr_rds_panel_0 = rds.rdsPanel(freq, self.GetWin())
        self.Add(self.gr_rds_panel_0.panel)
        self.gr_rds_decoder_0 = rds.decoder(False, False)
        self.freq_xlating_fir_filter_xxx_1 = filter.freq_xlating_fir_filter_fcc(audio_decim, (firdes.low_pass(2500.0,baseband_rate,2.4e3,2e3,firdes.WIN_HAMMING)), 57e3, baseband_rate)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, (firdes.low_pass(1, samp_rate, xlate_bandwidth, 100000)), freq_offset, samp_rate)
        self.digital_mpsk_receiver_cc_0 = digital.mpsk_receiver_cc(2, 0, 1*cmath.pi/100.0, -0.06, 0.06, 0.5, 0.05, samp_rate/bb_decim/audio_decim/ 2375.0, 0.001, 0.005)
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_char*1, 2)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=samp_rate,
        	audio_decimation=bb_decim,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.wxgui_fftsink2_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.analog_wfm_rcv_0, 0), (self.freq_xlating_fir_filter_xxx_1, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_1, 0), (self.wxgui_fftsink2_0_0_0_1_0_1, 0))
        self.connect((self.digital_mpsk_receiver_cc_0, 0), (self.wxgui_scopesink2_1, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_1, 0), (self.root_raised_cosine_filter_0, 0))
        self.connect((self.root_raised_cosine_filter_0, 0), (self.digital_mpsk_receiver_cc_0, 0))
        self.connect((self.digital_mpsk_receiver_cc_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.rtl_sdr_source0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.gr_rds_decoder_0, 0))

        ##################################################
        # Asynch Message Connections
        ##################################################
        self.msg_connect(self.gr_rds_decoder_0, "out", self.gr_rds_parser_0, "in")
        self.msg_connect(self.gr_rds_parser_0, "out", self.gr_rds_panel_0, "in")


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_baseband_rate(self.samp_rate/self.bb_decim)
        self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.samp_rate, self.xlate_bandwidth, 100000)))
        self.rtl_sdr_source0.set_sample_rate(self.samp_rate)
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate/self.bb_decim/self.audio_decim, 2375, 1, 100))
        self.digital_mpsk_receiver_cc_0.set_omega(self.samp_rate/self.bb_decim/self.audio_decim/ 2375.0)

    def get_bb_decim(self):
        return self.bb_decim

    def set_bb_decim(self, bb_decim):
        self.bb_decim = bb_decim
        self.set_baseband_rate(self.samp_rate/self.bb_decim)
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate/self.bb_decim/self.audio_decim, 2375, 1, 100))
        self.digital_mpsk_receiver_cc_0.set_omega(self.samp_rate/self.bb_decim/self.audio_decim/ 2375.0)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.set_freq_tune(self.freq - self.freq_offset)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.freq_offset)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.set_freq_tune(self.freq - self.freq_offset)
        self.gr_rds_panel_0.set_frequency(self.freq);

    def get_baseband_rate(self):
        return self.baseband_rate

    def set_baseband_rate(self, baseband_rate):
        self.baseband_rate = baseband_rate
        self.set_audio_decim_rate(self.baseband_rate/self.audio_decim)
        self.freq_xlating_fir_filter_xxx_1.set_taps((firdes.low_pass(2500.0,self.baseband_rate,2.4e3,2e3,firdes.WIN_HAMMING)))

    def get_audio_decim(self):
        return self.audio_decim

    def set_audio_decim(self, audio_decim):
        self.audio_decim = audio_decim
        self.set_audio_decim_rate(self.baseband_rate/self.audio_decim)
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.samp_rate/self.bb_decim/self.audio_decim, 2375, 1, 100))
        self.digital_mpsk_receiver_cc_0.set_omega(self.samp_rate/self.bb_decim/self.audio_decim/ 2375.0)

    def get_xlate_bandwidth(self):
        return self.xlate_bandwidth

    def set_xlate_bandwidth(self, xlate_bandwidth):
        self.xlate_bandwidth = xlate_bandwidth
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.samp_rate, self.xlate_bandwidth, 100000)))

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.rtl_sdr_source0.set_gain(self.gain, 0)

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.rtl_sdr_source0.set_center_freq(self.freq_tune, 0)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.wxgui_fftsink2_0_0_0_1_0_1.set_sample_rate(self.audio_rate)

    def get_audio_decim_rate(self):
        return self.audio_decim_rate

    def set_audio_decim_rate(self, audio_decim_rate):
        self.audio_decim_rate = audio_decim_rate

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = rds_rx()
    tb.Start(True)
    tb.Wait()
