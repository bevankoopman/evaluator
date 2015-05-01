#!/usr/bin/env python

import argparse
from math import sqrt

def read_ground_truth(ground_truth_file, icd):
	gt = {}
	with open(ground_truth_file) as fh:
		for line in fh:
			docId, classification = line.split()
			if icd:
				classification = classification[0:3]
			gt[docId] = classification
	return gt

class ConfusionMatrix():
	

	"""ConfusionMatrix for a single class"""
	def __init__(self, classification):
		self.classification = classification
		self.true_positive = 0
		self.false_positive = 0
		#self.true_negative = -1
		self.false_negative = 0

	def increment_true_positive(self):
		self.true_positive = self.true_positive + 1

	def increment_false_positive(self):
		self.false_positive = self.false_positive + 1

	def increment_true_negative(self):
		self.true_negative = self.true_negative + 1

	def increment_false_negative(self):
		self.false_negative = self.false_negative + 1

	def recall(self):
		try:
			return self.true_positive / float(self.true_positive + self.false_negative)
		except:
			return 0.0000

	def precision(self):

		try:
			return self.true_positive / float(self.true_positive + self.false_positive)
		except:
			return 0.0000

	def fmeasure(self):
		try:
			return 2 * self.precision() * self.recall() / (self.precision() + self.recall())
		except:
			return 0.0000

	def ci_precision(self):
		return self.conf_int(self.precision(), (self.true_positive+self.false_positive))

	def ci_recall(self):
		return self.conf_int(self.recall(), (self.true_positive+self.false_negative))

	def ci_fmeasure(self):
		return self.conf_int(self.fmeasure(), (self.true_positive+self.false_negative+self.false_positive))

	def __str__(self):
		tostring = ""
		tostring = tostring + "%s results:\n" % self.classification
		tostring = tostring + "\t\t\tClassifier\n"
		tostring = tostring + "\t\t\t-\t+\n"
		tostring = tostring + "\tGround\t-\t%d\t%d\n" % (self.true_negative, self.false_positive)
		tostring = tostring + "\tTruth\t+\t%d\t%d\n" % (self.false_negative, self.true_positive)
		tostring = tostring + "\n"
		return tostring

	def conf_int(self, p, n, z=1.96):
		return z * sqrt( (1/float(n)) * p * (1-p) )

	def summary_measures(self):		

		print "\t%s Precsion:\t%.4f\t95C.I.: %.4f-%.4f" % (self.classification, self.precision(), self.precision()-self.ci_precision(), self.precision()+self.ci_precision())
		print "\t%s Recall:\t%.4f\t95C.I.: %.4f-%.4f" % (self.classification, self.recall(), self.recall()-self.ci_recall(), self.recall()+self.ci_recall())
		print "\t%s Fmeasure:\t%.4f\t95C.I.: %.4f-%.4f" % (self.classification, self.fmeasure(), self.fmeasure()-self.ci_fmeasure(), self.fmeasure()+self.ci_fmeasure())

def get_binary_predictions(binary_prediction_file, weka=False):
	binary = {}
	if weka:
		start_prediction = False
		for line in open(binary_prediction_file):
			if start_prediction:
				items = line.split()
				if len(items) == 4:
					docid, coding = items[0:2]
					binary[docid.replace(".json", "")] = "0" if coding == "nocancer" or coding == "other" else coding
			if line.startswith("==Predictions=="):
				start_prediction = True
	else:
		for line in open(binary_prediction_file):
			items = line.split()
			docId = items[0]
			cancer = items[1] if len(items) > 1 else "0"
			binary[docId] = cancer
	
	return binary


def read_predictions(prediction_file, icd, weka):
	with open(prediction_file) as fh:
		predictions = False
		for line in fh:
			if weka:
				if predictions and not line.startswith("Total"):
					docId, pred, prob_prid, prob_not = line.split()
					predictions = [pred]
					yield docId.replace(".json", ""), predictions
				if line.startswith("==Predictions=="):
					predictions = True
			else:
				items = line.split()
				docId = items[0]
				predictions = [p.strip() for p in items[1:]]

				yield docId, predictions


if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description="Evaluate the predictions against ground truth.")
	argparser.add_argument("-p", "--prediction_file", required=True, help="Predictions file.")
	argparser.add_argument("-g", "--ground_truth_file", required=True, help="Ground truth file.")
	argparser.add_argument("-b", "--binary_prediction_file", required=False, help="Binary prediction to filter the prediction_file.")
	argparser.add_argument("-bw", "--binary_weka", action='store_true', default=False, help="Binary prediction is in Weka format.")
	argparser.add_argument('--icd', action='store_true', default=False, help="Whether the evaluation is using ICD code; in which case consider only first three characters (CXX). Default is False")
	argparser.add_argument("-t", '--tex', action='store_true', default=False, help="Print results in LaTeX table format.")
	argparser.add_argument("-w", '--weka', action='store_true', default=False, help="Predictions are in weka format")

	prediction_file = argparser.parse_args().prediction_file
	ground_truth_file = argparser.parse_args().ground_truth_file
	binary_prediction_file = argparser.parse_args().binary_prediction_file
	icd = argparser.parse_args().icd
	latex = argparser.parse_args().tex
	weka = argparser.parse_args().weka
	binary_weka = argparser.parse_args().binary_weka

	gt = read_ground_truth(ground_truth_file, icd)
	binary = {}
	if binary_prediction_file:
		binary = get_binary_predictions(binary_prediction_file, binary_weka)

	confusion_matices = {}

	print "docId\tActual\tPredictions (1..n) *=correct"
	pred_count = 0
	for docId, predictions in read_predictions(prediction_file, icd, weka):
		pred_count = pred_count + 1

		binary_comment = ""
		if len(binary) > 0 and binary[docId] == "0":
			for p in predictions:
				if p != "other" and p != "nocancer":
					binary_comment = binary_comment + " " + p +"->other"
			predictions = ["other"]

		conf_mat = confusion_matices.get(gt[docId], ConfusionMatrix(gt[docId]))

		correct = False
		for prediction in predictions:
			if icd:
				prediction = prediction[0:3]
			if prediction == gt[docId]:
				correct = True
				conf_mat.increment_true_positive()
				break
		confusion_matices[gt[docId]] = conf_mat

		labeled_predictions = [p+('*' if p == gt[docId] else "") for p in predictions]

		print "%s\t%s\t%s\t%s" % (docId, gt[docId], reduce(lambda x,y: x+"\t"+y, labeled_predictions), binary_comment)

		if not correct:
			for prediction in predictions:
				conf_mat.increment_false_negative()
				other_conf_matrix = confusion_matices.get(prediction, ConfusionMatrix(prediction))
				other_conf_matrix.increment_false_positive()
				confusion_matices[prediction] = other_conf_matrix
	
	print "\n== SUMMARY ==\n"
	for conf_mat in confusion_matices.values():
		conf_mat.true_negative = pred_count - conf_mat.true_positive - conf_mat.false_positive - conf_mat.false_negative
		print conf_mat
		conf_mat.summary_measures()
		print ""
		#print conf_mat.classification, conf_mat.precision(), conf_mat.recall(), conf_mat.fmeasure(), conf_mat.true_positive, conf_mat.false_positive

	if latex:
		print '''
\\begin{table}
 \\small
 \\centering
 \\begin{tabular}{lrrr|rrcl}
 \\toprule	
 \\bf Disease &  \\bf Precision & \\bf Recall & \\bf F-measure & \multicolumn{4}{c}{\\bf Confusion Matrix} \\\\
 & & & & \multicolumn{2}{r}{Classifier} & \multicolumn{2}{r}{Ground truth} \\\\
 & & & & - & +  \\\\
 \\midrule '''
		for conf_mat in confusion_matices.values():
			print " %s & %.4f & %.4f & %.4f & %d & %d & - \\\\" % (conf_mat.classification, conf_mat.precision(), conf_mat.recall(), conf_mat.fmeasure(), conf_mat.true_negative, conf_mat.false_positive)
			print " & & & & %d & %d & + & %s \\\\" % (conf_mat.false_negative, conf_mat.true_positive, conf_mat.classification)
		print '''\\bottomrule
 \\end{tabular}
 \\caption{Classification evaluation.}
 \\label{tbl:results}
\\end{table}
'''

