# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Fraunhofer FKIE/US, Alexander Tiderko
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of I Heart Engineering nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from PySide import QtCore, QtGui

import roslib
import rospy
import node_manager_fkie as nm

from parameter_handler import ParameterHandler

class ParameterDialog(QtGui.QDialog):
  '''
  This dialog creates an input mask for the given slots and their types.
  '''

  def __init__(self, params, buttons=QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok, parent=None):
    '''
    Creates an input dialog.
    @param slots: a list with  slots to enter
    @type slots: C{[str, ...]}
    @param types: a list with  types of the slots
    @type types: C{[str, ...]}
    @param params: a dictionary with parameter names and (type, values). 
    The C{value}, can be a primitive value, a list with values or parameter 
    dictionary to create groups. In this case the type is the name of the group.
    @type params: C{dict(str:(str, {value, [..], dict()}))}
    '''
    QtGui.QDialog.__init__(self, parent=parent)
    self.setObjectName(' - '.join(['ParameterDialog', str(params)]))
    self.verticalLayout = QtGui.QVBoxLayout(self)
    self.verticalLayout.setObjectName("verticalLayout")
    self.verticalLayout.setContentsMargins(1, 1, 1, 1)
    
    self.filter_frame = QtGui.QFrame(self)
    filterLayout = QtGui.QHBoxLayout(self.filter_frame)
    filterLayout.setContentsMargins(1, 1, 1, 1)
    label = QtGui.QLabel("Filter:", self.filter_frame)
    self.filter_field = QtGui.QLineEdit(self.filter_frame)
    filterLayout.addWidget(label)
    filterLayout.addWidget(self.filter_field)
    self.filter_field.textChanged.connect(self._on_filter_changed)
    
    self.verticalLayout.addWidget(self.filter_frame)
    
    self.scrollArea = scrollArea = QtGui.QScrollArea(self);
    scrollArea.setObjectName("scrollArea")
    scrollArea.setWidgetResizable(True)
    self.content = QtGui.QWidget()
    self.content.setObjectName("scrollAreaWidgetContents")
    self.contentLayout = QtGui.QFormLayout(self.content)
    self.contentLayout.setVerticalSpacing(0)
#    self.contentLayout.setVerticalSpacing(0)
#    self.contentLayout.setHorizontalSpacing(1)
    scrollArea.setWidget(self.content)
  
    self.verticalLayout.addWidget(scrollArea)

#    self.content.setLayout(self.contentLayout)
    self.buttonBox = QtGui.QDialogButtonBox(self)
    self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
    self.buttonBox.setStandardButtons(buttons)
    self.buttonBox.setObjectName("buttonBox")
    self.verticalLayout.addWidget(self.buttonBox)

    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
    QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
    QtCore.QMetaObject.connectSlotsByName(self)

    # add info text field
    self.info_field = QtGui.QTextEdit(self.content)
    self.info_field.setVisible(False)
    palette = QtGui.QPalette()
    brush = QtGui.QBrush(QtGui.QColor(255, 254, 242))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
    brush = QtGui.QBrush(QtGui.QColor(255, 254, 242))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
    brush = QtGui.QBrush(QtGui.QColor(244, 244, 244))
    brush.setStyle(QtCore.Qt.SolidPattern)
    palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
    self.info_field.setPalette(palette)
    self.info_field.setFrameShadow(QtGui.QFrame.Plain)
    self.info_field.setReadOnly(True)
    self.info_field.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
    self.info_field.setObjectName("dialog_info_field")

    # set the input fields
    self.params = list() # (field, type)
#    self.contentLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
    self._insertItems(self.content, self.contentLayout, params)
    if self.params:
      self.params[0][1].setFocus(QtCore.Qt.OtherFocusReason)
      
    self.filter_visible = True
#    print '=============== create', self.objectName()

#  def __del__(self):
#    print "************ destroy", self.objectName()

  def _on_filter_changed(self):
    for type, field in self.params:
      if field.objectName().lower().find(self.filter_field.text().lower()) == -1:
        label = field.parentWidget().layout().labelForField(field)
        field.setVisible(False)
        label.setVisible(False)
      else:
        label = field.parentWidget().layout().labelForField(field)
        field.setVisible(True)
        label.setVisible(True)
      self.contentLayout.update()

  def setFilterVisible(self, val):
    self.filter_visible = val
    self.filter_frame.setVisible(val&self.scrollArea.isHidden())


  def setText(self, text):
    '''
    Adds a label to the dialog's layout and shows the given text.
    @param text: the text to add to the dialog
    @type text: C{str}
    '''
    self.info_field.setText(text)
    self.setInfoActive(True)

  def setInfoActive(self, val):
    if val and self.info_field.isHidden():
      self.filter_frame.setVisible(False&self.filter_visible)
      self.scrollArea.setVisible(False)
      self.info_field.setVisible(True)
      self.verticalLayout.removeWidget(self.buttonBox)
      self.verticalLayout.removeWidget(self.filter_frame)
      self.verticalLayout.removeWidget(self.scrollArea)
      self.verticalLayout.removeWidget(self.info_field)
      self.verticalLayout.addWidget(self.info_field)
      self.verticalLayout.addWidget(self.buttonBox)
    elif not val and self.scrollArea.isHidden():
      self.filter_frame.setVisible(True&self.filter_visible)
      self.scrollArea.setVisible(True)
      self.info_field.setVisible(False)
      self.verticalLayout.removeWidget(self.filter_frame)
      self.verticalLayout.removeWidget(self.buttonBox)
      self.verticalLayout.removeWidget(self.scrollArea)
      self.verticalLayout.removeWidget(self.info_field)
      self.verticalLayout.addWidget(self.filter_frame)
      self.verticalLayout.addWidget(self.scrollArea)
      self.verticalLayout.addWidget(self.buttonBox)

  def _insertItems(self, parent, layout, params, ns=''):
    '''
    Adds input fields to the layout of the dialog.
    @param params: a dictionary with parameter names and (type, values). 
    The C{value}, can be a primitive value, a list with values or parameter 
    dictionary to create groups. In this case the type is the name of the group.
    @type params: C{dict(str:(str, {value, [..], dict()}))}
    '''
    self.setInfoActive(False)
    for name, (type, value) in sorted(params.items()):
      full_name = roslib.names.ns_join(ns, name) if ns else name
      base_type = roslib.msgs.base_msg_type(type)
      if isinstance(value, dict):
        box = QtGui.QGroupBox(type, parent)
        boxLayout = QtGui.QFormLayout(box)
        box.setObjectName(type)
        namespace = roslib.names.ns_join(ns, type) if ns else type
        self._insertItems(box, boxLayout, value, namespace)
        box.setLayout(boxLayout)
        layout.addRow(box)
      elif base_type in roslib.msgs.PRIMITIVE_TYPES or base_type in ['int', 'float'] and not isinstance(value, dict):
        if base_type == 'bool':
          field = QtGui.QCheckBox(parent)
          if isinstance(value, bool):
            field.setChecked(value)
        else:
          field = QtGui.QComboBox(parent)
          field.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed))
          field.setEditable(True)
          items = []
          cache = []
          if nm.PARAM_CACHE.has_key(full_name):
            cache[len(cache):] = [unicode(v) for v in nm.PARAM_CACHE[full_name]] 
          if isinstance(value, list):
            items[len(items):] = value
          else:
            items.append(unicode(value))
            self.addParamCache(full_name, unicode(value))
          field.addItems(items)
          field.addItems(list(set(cache)-set(items)))
        field.setObjectName(full_name)
        label_name = name if type == 'string' else ''.join([name, ' (', type, ')'])
        label = QtGui.QLabel(label_name, parent)
        label.setObjectName(''.join([full_name, '_label']))
        label.setBuddy(field)
        layout.addRow(label, field)
        self.params.append((type, field))

  def getKeywords(self):
    '''
    @returns: a directory with parameter and value for all entered fields.
    @rtype: C{dict(str(param) : str(value))}
    '''
    result = {}
    for type, field in self.params:
      if isinstance(field, QtGui.QCheckBox):
        result[field.objectName()] = field.isChecked()
      else:
        test = ''
        if isinstance(field, QtGui.QLineEdit):
          text = field.text()
        elif isinstance(field, QtGui.QComboBox):
          text = field.currentText()
        if text:
          if 'int' in type:
            result[field.objectName()] = int(text)
          elif 'float' in type:
            result[field.objectName()] = float(text)
          else:
            result[field.objectName()] = text
          self.addParamCache(field.objectName(), text)
    return result
  
  def addParamCache(self, key, value):
    if not nm.PARAM_CACHE.has_key(key):
      nm.PARAM_CACHE[key] = [value]
    elif not key in nm.PARAM_CACHE[key]:
      nm.PARAM_CACHE[key].append(value)


class ThreadedParameterDialog(ParameterDialog):
  
  def __init__(self, masteruri, ns='/', buttons=QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok, parent=None):
    ParameterDialog.__init__(self, dict(), buttons, parent=parent)
    self.setObjectName(' - '.join(['ThreadedParameterDialog', masteruri, ns]))
    self.masteruri = masteruri
    self.ns = ns
#    self.setWindowFlags(QtCore.Qt.Window)
    self.resize(450,300)
    self.mIcon = QtGui.QIcon(":/icons/crystal_clear_default_cfg.png")
    self.setWindowIcon(self.mIcon)
    self.setText(' '.join(['Obtaining parameters from the parameter server', masteruri, '...']))
    self.parameterHandler = ParameterHandler()
    self.parameterHandler.parameter_list_signal.connect(self._on_param_list)
    self.parameterHandler.parameter_values_signal.connect(self._on_param_values)
    self.parameterHandler.delivery_result_signal.connect(self._on_delivered_values)

    self.add_new_button = QtGui.QPushButton(self.tr("&Add"))
    self.buttonBox.addButton(self.add_new_button, QtGui.QDialogButtonBox.ActionRole)
    self.buttonBox.clicked.connect(self.on_clicked)
    
    self.is_delivered = False
    self.is_send = False
    self.parameterHandler.requestParameterList(masteruri, ns)
#    print '=============== create', self.objectName()

#  def __del__(self):
#    print "************ destroy", self.objectName()

  def on_clicked(self, button):
    if button == self.add_new_button:
      params = {'namespace' : ('string', self.ns), 'name' : ('string', ''), 'type' : ('string', ['string', 'int', 'float', 'bool']), 'value' : ('string', '') }
      dia = ParameterDialog(params)
      dia.setFilterVisible(False)
      if dia.exec_():
        params = dia.getKeywords()
        try:
          if params['type'] == 'int':
            value = int(params['value'])
          elif params['type'] == 'float':
            value = float(params['value'])
          elif params['type'] == 'bool':
            value = bool(params['value'])
          else:
            value = params['value']
          self._on_param_values(self.masteruri, 1, '', {roslib.names.ns_join(params['namespace'], params['name']) : (1, '', value)})
        except ValueError, e:
          QtGui.QMessageBox.warning(self, self.tr("Warning"), unicode(e), QtGui.QMessageBox.Ok)

  def _on_param_list(self, masteruri, code, msg, params):
    '''
    @param masteruri: The URI of the ROS parameter server
    @type masteruri: C{str}
    @param code: The return code of the request. If not 1, the message is set and the list can be ignored.
    @type code: C{int}
    @param msg: The message of the result. 
    @type msg: C{str}
    @param params: The list the parameter names.
    @type param: C{[str]}
    '''
    if code == 1:
      params.sort()
      self.parameterHandler.requestParameterValues(masteruri, params)
    else:
      self.setText(msg)
      
  def _on_param_values(self, masteruri, code, msg, params):
    '''
    @param masteruri: The URI of the ROS parameter server
    @type masteruri: C{str}
    @param code: The return code of the request. If not 1, the message is set and the list can be ignored.
    @type code: C{int}
    @param msg: The message of the result. 
    @type msg: C{str}
    @param params: The dictionary the parameter names and request result.
    @type param: C{dict(paramName : (code, statusMessage, parameterValue))}
    '''
    if code == 1:
      self.setText('')
      values = dict()
      dia_params = dict()
      for p, (code_n, msg_n, val) in params.items():
        if code_n != 1:
          val = ''
        type_str = 'string'
        value = val
        if isinstance(val, bool):
          type_str = 'bool'
        elif isinstance(val, int):
          type_str = 'int'
        elif isinstance(val, float):
          type_str = 'float'
        elif isinstance(val, list) or isinstance(val, dict):
          value = unicode(val)
        param = p.replace(self.ns, '')
        names_sep = param.split(roslib.names.SEP)
        param_name = names_sep.pop()
        if names_sep:
          group = dict()
          for n in names_sep:
            group_name = '_'.join([n, 'group'])
            if dia_params.has_key(group_name):
              group = dia_params[group_name][1]
            else:
              group = dict()
              dia_params[group_name] = (n, group)
          group[param_name] = (type_str, value)
        else:
          dia_params[param_name] = (type_str, value)
      self._insertItems(self.content, self.contentLayout, dia_params)
      if self.params:
        self.params[0][1].setFocus(QtCore.Qt.OtherFocusReason)
    else:
      self.setText(msg)

  def _on_delivered_values(self, masteruri, code, msg, params):
    '''
    @param masteruri: The URI of the ROS parameter server
    @type masteruri: C{str}
    @param code: The return code of the request. If not 1, the message is set and the list can be ignored.
    @type code: C{int}
    @param msg: The message of the result. 
    @type msg: C{str}
    @param params: The dictionary the parameter names and request result.
    @type param: C{dict(paramName : (code, statusMessage, parameterValue))}
    '''
    self.is_delivered = True
    errmsg = ''
    if code == 1:
      for p, (code_n, msg, val) in params.items():
        if code_n != 1:
          errmsg = '\n'.join([errmsg, msg])
    else:
      errmsg = msg if msg else 'Unknown error on set parameter'
    if errmsg:
      QtGui.QMessageBox.warning(self, self.tr("Warning"), errmsg, QtGui.QMessageBox.Ok)
      self.is_delivered = False
      self.is_send = False
      self.setInfoActive(False)
    if self.is_delivered:
      self.close()

  def accept(self):
    '''
    Push the values to the ROS parameter server.
    '''
    if not self.is_send:
      try:
        params = self.getKeywords()
        res_params = dict()
        for p,v in params.items():
          res_params[roslib.names.ns_join(self.ns, p)] = v
        self.is_send = True
        self.setText('Load the parameter into server...')
        self.parameterHandler.deliverParameter(self.masteruri, res_params)
      except ValueError, e:
        QtGui.QMessageBox.warning(self, self.tr("Warning"), str(e), QtGui.QMessageBox.Ok)
#    QtGuit.QDialog.accept()

  def reject(self):
    self.is_send = False
    ParameterDialog.reject(self)
  
  def hideEvent(self, event):
    if not (self.is_send and not self.is_delivered):
      self.setParent(None)
      self.close()