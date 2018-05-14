#!/usr/bin/python
#
# Copyright (C) 2017 geeks-r-us.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may find one here:
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# or you may search the http://www.gnu.org website for the version 2 license,
# or you may write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#

from pcbnew import *
import HelpfulFootprintWizardPlugin as HFPW
import math


class CapacitivTouchWizard(HFPW.HelpfulFootprintWizardPlugin):
    def GetName(self):
        """
        Return footprint name.
        This is specific to each footprint class, you need to implement this
        """
        return 'Capacitiv Touch Sensor'

    def GetDescription(self):
        """
        Return footprint description.
        This is specific to each footprint class, you need to implement this
        """
        return 'Capacitive Touchpad wizard'

    def GetValue(self):
        prms = self.parameters["Pads"]
        diamondsX = prms["*diamondsX"]
        diamondsY = prms["*diamondsY"]
        return "TS" + str(diamondsX) + "x" + str(diamondsY)

    def GenerateParameterList(self):
        self.AddParam("Pads", "diamondsX", self.uNatural, 4)
        self.AddParam("Pads", "diamondsY", self.uNatural, 2)
        self.AddParam("Pads", "diameter", self.uMM, 6)
        self.AddParam("Pads", "clearance", self.uMM, 0.2)
        self.AddParam("Pads", "via", self.uMM, 0.3)
        self.AddParam("Pads", "viadistance", self.uMM, 0.5)

    # build a rectangular pad
    def smdRectPad(self, size, pos, name, orientation = 450, layer = F_Cu):
        pad = D_PAD(self.module)
        pad.SetSize(size)
        pad.SetShape(PAD_SHAPE_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetLayer(layer)
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetPadName(name)
        pad.SetOrientation(orientation)
        return pad

    def track(self, size, pos, name, orientation = 450, layer = F_Cu):
        pad = D_PAD(self.module)
        pad.SetSize(size)
        pad.SetShape(PAD_SHAPE_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetLayer(layer)
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetPadName(name)
        pad.SetOrientation(orientation)
        return pad

    def smdTrianglePad(self, size, pos, name, up_down=1, left_right=0):
        pad = D_PAD(self.module)
        pad.SetSize(size)
        pad.SetShape(PAD_SHAPE_TRAPEZOID)
        pad.SetAttribute(PAD_ATTRIB_SMD)
        pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetPadName(name)
        orientation = wxSize(left_right * size[0], up_down * size[1])
        pad.SetDelta(orientation)
        return pad

    def THRoundPad(self, position, name, drill ):
        pad = D_PAD(self.module)
        pad.SetSize(wxSize(drill*2, drill*2))
        pad.SetShape(PAD_SHAPE_CIRCLE)
        pad.SetAttribute(PAD_ATTRIB_STANDARD)
        pad.SetDrillSize(wxSize(drill, drill))
        pad.SetLayerSet(pad.StandardMask())
        pad.SetPosition(position)
        pad.SetPos0(position)
        pad.SetPadName(name)
        return pad

    def Via(self, position, drill):
        via = VIA(self.module)
        #via.SetSize(wxSize(drill*2, drill*2))
        via.SetViaType( VIA_THROUGH_VISIBLE)
        via.SetPosition(position)
        via.SetDrill(drill)
        return via;


    # This method checks the parameters provided to wizard and set errors
    def CheckParameters(self):
        prms = self.parameters["Pads"]
        diamondsX = prms["*diamondsX"]
        diamondsY = prms["*diamondsY"]

        if diamondsX < 1:
            self.parameter_errors["Pads"]["*steps"] = "diamondsX must be positive"
        if diamondsY < 1:
            self.parameter_errors["Pads"]["*bands"] = "diamondsY must be positive"

        touch_diameter = prms["diameter"]
        touch_clearance = prms["clearance"]

        if touch_diameter < FromMM(4) or touch_diameter > FromMM(10):
            self.parameter_errors["Pads"]["diameter"] = "diameter must be between 4 - 10 mm"

    def AddDiamond(self, position, name):
        touch_diameter = self.parameters["Pads"]["diameter"]
        size_rotated = math.sqrt(touch_diameter ** 2 / 2)
        size_pad = wxSize(size_rotated, size_rotated)
        pad = self.smdRectPad(size_pad, position, name)
        self.module.Add(pad)

    def AddHalfDiamond(self, position, name, up_down=1, left_right=0):
        touch_diameter = self.parameters["Pads"]["diameter"]

        size_rotated = touch_diameter / 2
        size_pad = wxSize(size_rotated, size_rotated)

        pos_translate = wxPoint(-left_right * touch_diameter / 4, up_down * touch_diameter / 4)

        pad = self.smdTrianglePad(size_pad, position - pos_translate, name, up_down, left_right)
        self.module.Add(pad)

    def AddBar(self, position, name, layer):
        touch_diameter = self.parameters["Pads"]["diameter"]
        touch_clearance = self.parameters["Pads"]["clearance"]
        touch_via = self.parameters["Pads"]["via"]
        touch_via_distance = self.parameters["Pads"]["viadistance"]
        if layer == B_Cu:
            size = wxSize(touch_clearance + touch_via_distance * 2, touch_clearance / 4)
            midoffset = wxPoint(touch_clearance/2 + touch_diameter/2,0)
            viaoffset = wxPoint(touch_clearance + touch_via_distance,0)

            track1 = TRACK(self.module)
            track1.SetStart(position - midoffset)
            track1.SetEnd(position - viaoffset)
            track1.SetLayer(F_Cu)
            track1.SetWidth(touch_clearance / 4)

            self.module.Add(track1)

            via1 = self.Via(position - viaoffset, touch_via)
            self.module.Add(via1)

            track2 = TRACK(self.module)
            track2.SetStart(position - viaoffset)
            track2.SetEnd(position + viaoffset)
            track2.SetLayer(B_Cu)
            track2.SetWidth(touch_clearance / 4)

            self.module.Add(track2)

            via2 = self.Via(position + viaoffset, touch_via)
            self.module.Add(via2)

            track3 = TRACK(self.module)
            track3.SetStart(position + viaoffset)
            track3.SetEnd(position + midoffset)
            track3.SetLayer(F_Cu)
            track3.SetWidth(touch_clearance / 4)

            self.module.Add(track3)

            # pad = self.smdRectPad(size, position, name, 0, layer)

            # cubSet = LSET(1,B_Cu)
            # pad.SetLayerSet(cubSet)

            #self.module.Add(pad)
            #translate = wxPoint(touch_clearance + touch_via_distance,0)
            #via1 = self.THRoundPad(position + translate, name, touch_via)
            #self.module.Add(via1)
            #via2 = self.THRoundPad(position - translate, name, touch_via)
            #self.module.Add(via2)

        else :

            midoffset = wxPoint(0,touch_clearance/2 + touch_diameter/2)
            track1 = TRACK(self.module)
            track1.SetStart(position - midoffset)
            track1.SetEnd(position + midoffset)
            track1.SetWidth(touch_clearance / 4)
            track1.SetLayer(F_Cu)
            self.module.Add(track1)

            #size = wxSize(touch_clearance * 2, touch_clearance / 4)
            #pad = self.smdRectPad(size, position, name, 900, layer)
            #self.module.Add(pad)


    # build the footprint from parameters
    def BuildThisFootprint(self):
        prm = self.parameters["Pads"]
        diamondsX = int(prm["*diamondsX"])
        diamondsY = int(prm["*diamondsY"])
        touch_diameter = prm["diameter"]
        touch_clearance = prm["clearance"]

        t_size = self.GetTextSize()
        w_text = self.draw.GetLineTickness()

        fullsize = touch_diameter + touch_clearance

        for x in range(1, diamondsX):
            for y in range(0, diamondsY):
                pos = wxPoint(x * fullsize, y * fullsize + fullsize / 2)
                self.AddDiamond(pos, "foo" + str(y))
                if x == 1:
                    self.AddHalfDiamond(wxPoint(0, fullsize / 2 + y * fullsize), "foo" + str(y), 0, 1)
                    self.AddHalfDiamond(wxPoint(diamondsX * fullsize, fullsize / 2 + y * fullsize), "foo" + str(y), 0,
                                        -1)


        for y in range(1, diamondsY):
            for x in range(0, diamondsX):
                pos = wxPoint(x * fullsize + fullsize / 2, y * fullsize)
                self.AddDiamond(pos, "bar" + str(x))
                if y == 1:
                    self.AddHalfDiamond(wxPoint(fullsize / 2 + x * fullsize, 0), "bar" + str(x), -1, 0)
                    self.AddHalfDiamond(wxPoint(fullsize / 2 + x * fullsize, diamondsY * fullsize), "bar" + str(x), 1,
                                        0)

        for y in range(0, diamondsY):
            for x in range(0, diamondsX):
                self.AddBar(wxPoint(fullsize / 2 + x * fullsize, y * fullsize + fullsize / 2),"foo"+str(y), B_Cu)
                self.AddBar(wxPoint(fullsize / 2 + x * fullsize, y * fullsize + fullsize / 2),"bar"+str(y), F_Cu)



CapacitivTouchWizard().register()
