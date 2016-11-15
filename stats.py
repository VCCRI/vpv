# Copyright 2016 Medical Research Council Harwell.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# @author Neil Horner <n.horner@har.mrc.ac.uk>


from PyQt4 import QtGui
from scipy import stats

import numpy as np
import SimpleITK as sitk

from ui.ui_stats import Ui_Stats


class StatsWidget(QtGui.QDialog):
    def __init__(self, parent, model):
        super(StatsWidget, self).__init__(parent)
        self.ui = Ui_Stats()
        self.ui.setupUi(self)
        self.setWindowTitle('Statisitics')
        self.model = model

        self.stats_available = {
            'ttest': Ttest,
            'Anova': Anova
        }

        self.ui.pushButtonCancel.clicked.connect(self.on_close)
        self.ui.pushButtonGo.clicked.connect(self.on_ok)
        self.ui.comboBoxStats.addItems(self.get_available_stats())
        self.set_available_data()

        #self.populate_widget()

    def on_close(self):
        self.close()

    def on_ok(self):
        """
        Get the data files and the method to do the test
        """

        # make sure a name for the analysis has been set  - should also check for duplicate names
        if len(str(self.ui.lineEditOutputName.text())) < 1:
            dialog = QtGui.QMessageBox.warning(self, '', 'Enter an output name',
                                               QtGui.QMessageBox.Cancel)
            return

        output_name = str(self.ui.lineEditOutputName.text())

        method = str(self.ui.comboBoxStats.currentText())
        baseline_name = str(self.ui.comboBoxBaseline.currentText())
        baseline = self.model.get_rawdata(baseline_name)
        testdata_name = str(self.ui.comboBoxTestData.currentText())
        testdata = self.model.get_rawdata(testdata_name)

        stat = self.get_stats_method(method)()

        #try:
        stat.set_baseline(baseline)
        stat.set_testdata(testdata)
        stat.check_data()
        results = stat.run_test()
        #except TypeError as e:
        #    print e
        #    QtGui.QMessageBox.warning(self, '', 'Stats error: {}'.format(e),
           #                           QtGui.QMessageBox.Cancel)
        #else:
        self.model.add_processed_data(results, output_name, baseline, testdata)

        self.close()

    def get_stats_method(self, name):
        return self.stats_available[str(name)]

    def get_available_stats(self):
        return [key for key in self.stats_available]

    def set_available_data(self):
        data_list = self.model.rawdata_id_list()
        self.ui.comboBoxBaseline.addItems(data_list)
        self.ui.comboBoxTestData.addItems(data_list)

    def set_available_stats(self, stats_list):
        self.ui.comboBoxStats.addItems(stats_list)


class AbstractStats(object):
    def __init__(self):
        self.baseline = None  # RawData
        self.testdata = None  # RawData

    def set_baseline(self, baseline):
        self.baseline = baseline

    def set_testdata(self, test_data):
        self.testdata = test_data

    def check_data(self):
        if self.baseline.data['data_type'] != self.testdata.data['data_type']:
            raise TypeError("Looks like you are compariing different data types. "
                            "Jacobians and deformation vectors maybe")

        if self.baseline.data['chunksize'] != self.testdata.data['chunksize']:
            raise TypeError("the input data files do not have the same chunck size. Remake them")

        if self.baseline.data['deform_dimensions'] != self.testdata.data['deform_dimensions']:
            raise TypeError("the input data files do not have the same dimensions. Remake them")

    def run_test(self):
        raise NotImplementedError("Subclasses should implement this!")


class Ttest(AbstractStats):
    def __init__(self):
        super(Ttest, self).__init__()
        self.name = 'ttest'

    def run_test(self):
        """
        Do a ttest on each position. Save the results in a numpy array.
        As a test this array will be used for generating a 2d slice to superimpose on the volumes.
        Not sure if it will be fast enough yet
        """

        wt_means = self.baseline.data['data']  # => OrderedDict
        mut_means = self.testdata.data['data']  # => OrderedDict
        dimensions = self.baseline.data['deform_dimensions'][0:3]
        chunksize = self.baseline.data['chunksize']

        # Create an array with the same dimensions as the original data
        z = dimensions[0]
        y = dimensions[1]
        x = dimensions[2]
        pval_array = np.zeros((z, y, x), dtype=np.float32)   # float16 crashes sitk.GetImageFromArray()

        # Ceate the pvalue array
        for wt_pos, mut_pos in zip(wt_means, mut_means):
            assert wt_pos == mut_pos  # Esure we have corresponding positions
            pvalue = self.ttest(wt_means[wt_pos], mut_means[mut_pos])
            pval_array[wt_pos[0]: wt_pos[0] + chunksize,
                       wt_pos[1]: wt_pos[1] + chunksize,
                       wt_pos[2]: wt_pos[2] + chunksize] = pvalue

        img = sitk.GetImageFromArray(pval_array)
        sitk.WriteImage(img, '/home/neil/testout.nrrd')

        return pval_array

    def ttest(self, wt, mut):
        """
        :param wt:
        :param mut:
        :return: float, pvalue
        """
        #Can't get scipy working on Idaho at the moment so use ttest from cogent package for now
        return stats.ttest_ind(mut, wt)[1]

class Anova(AbstractStats):
    def __init__(self):
        super(Ttest, self).__init__()
        self.name = 'ttest'


    def do_test(self):
        pass


