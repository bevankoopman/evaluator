#!/usr/bin/env python

import argparse

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
		self.true_negative = 0
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

	def __str__(self):
		tostring = ""
		tostring = tostring + "%s results" % self.classification
		tostring = tostring + "\t\t\tClassifier\n"
		tostring = tostring + "\t\t\t-\t+\n"
		tostring = tostring + "\tGround\t-\t%d\t%d\n" % (self.true_negative, self.false_positive)
		tostring = tostring + "\tTruth\t+\t%d\t%d\n" % (self.false_negative, self.true_positive)
		tostring = tostring + "\n"
		return tostring

	def summary_measures(self):
		print "%s Recall: %.4f" % (self.classification, self.recall())
		print "%s Precsion: %.4f" % (self.classification, self.precision())
		print "%s Fmeasure: %.4f" % (self.classification, self.fmeasure())

def get_binary_predictions(binary_prediction_file):
	binary = {}
	for line in open(binary_prediction_file):
		items = line.split()
		docId = items[0]
		cancer = items[1] if len(items) > 1 else "0"
		binary[docId] = cancer
	return binary

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description="Evaluate the predictions against ground truth.")
	argparser.add_argument("-p", "--prediction_file", required=True, help="Predictions file.")
	argparser.add_argument("-g", "--ground_truth_file", required=True, help="Ground truth file.")
	argparser.add_argument("-b", "--binary_prediction_file", required=False, help="Binary prediction to filter the prediction_file on.")
	argparser.add_argument('--icd', action='store_true', default=False, help="Whether the evaluation is using ICD code; in which case consider only first three characters (CXX). Default is False")

	prediction_file = argparser.parse_args().prediction_file
	ground_truth_file = argparser.parse_args().ground_truth_file
	binary_prediction_file = argparser.parse_args().binary_prediction_file
	icd = argparser.parse_args().icd

	gt = read_ground_truth(ground_truth_file, icd)
	binary = {}
	if binary_prediction_file:
		binary = get_binary_predictions(binary_prediction_file)
	
	confusion_matices = {}

	with open(prediction_file) as fh:
		for line in fh:
			items = line.split()
			docId = items[0]
			predictions = [p.strip() for p in items[1:]]

			if len(binary) > 0 and binary[docId] == "0":
				continue

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

			print docId, gt[docId], [p+('*' if p == gt[docId] else "") for p in predictions]

			if not correct:
				for prediction in predictions:
					conf_mat.increment_false_negative()
					other_conf_matrix = confusion_matices.get(prediction, ConfusionMatrix(prediction))
					other_conf_matrix.increment_false_positive()
					confusion_matices[prediction] = other_conf_matrix
	
	for conf_mat in confusion_matices.values():
		print conf_mat
		conf_mat.summary_measures()
		print ""