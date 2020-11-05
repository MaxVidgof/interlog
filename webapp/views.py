from django.shortcuts import render
from datetime import datetime
import hashlib
import subprocess
from django.http import HttpResponse
import os
import pm4py
import json
import dateutil.parser
from django.core.serializers.json import DjangoJSONEncoder

#TODO: users map for garbage collection

def index(req):
	req.session["id"] = hashlib.sha256(bytes(str(req.META["REMOTE_ADDR"]) + str(datetime.now()), 'utf-8')).hexdigest()
	return render(req, "index.html", {"baseUrl": req.session["id"]})

def upload_log(req):
	print(req.FILES.keys())
	input_log_file = req.FILES["input_log_file"]
	subprocess.call(["rm", "-f", req.session["id"] + "_*"])
	with open(os.path.join("webapp","static", req.session["id"] + "_l0.xes"), 'wb') as file:
		file.write(input_log_file.read())
	input_file = os.path.join("webapp","static", req.session["id"] + "_l0.xes")
	from pm4py.objects.log.importer.xes import importer as xes_importer
	log = xes_importer.apply(input_file, variant = xes_importer.Variants.ITERPARSE, parameters = {xes_importer.Variants.ITERPARSE.value.Parameters.TIMESTAMP_SORT: True})
	from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
	heu_net = heuristics_miner.apply_heu(log, parameters={"dependency_thresh": 0.99})
	from pm4py.visualization.heuristics_net import visualizer as hn_vis_factory
	gviz = hn_vis_factory.apply(heu_net)
	hn_vis_factory.view(gviz)
	hn_vis_factory.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l0.png"))
	response = HttpResponse(json.dumps({'start_time': log[0][0]["time:timestamp"], 'end_time': log[-1][-1]["time:timestamp"]}, sort_keys=True, indent=1, cls=DjangoJSONEncoder))
	response.status_code = 200
	return response

def apply_filter(req):
	#print(str(req.body))
	o = json.loads(req.body)
	print(str(o))
	custom_time_range = []
	for pair in o["filter1"]:
		custom_time_range.append((dateutil.parser.parse(pair[0]),dateutil.parser.parse(pair[1])))
	#print(custom_time_range)
	custom_path_range = []
	for pair in o["filter2"]:
		custom_path_range.append((float(pair[0]),float(pair[1])))
	#print(str(custom_path_range))
	#custom_path_range = [(0,1)] #filter2
	custom_activitiy_range = []
	for pair in o["filter3"]:
		custom_activitiy_range.append((float(pair[0]),float(pair[1])))
	#custom_activitiy_range = [(0,1)] #filter3
	input_file = os.path.join("webapp","static", req.session["id"] + "_l0.xes")
	from pm4py.objects.log.importer.xes import importer as xes_importer
	input_log = xes_importer.apply(input_file)
	from pm4py.algo.filtering.log.variants import variants_filter

	time_timestamp_started = datetime.now()

	from pm4py.algo.filtering.log.timestamp import timestamp_filter
	#TODO check overlapping for filter
	logs = []
	for (x,y) in custom_time_range:
		logs.append(timestamp_filter.filter_traces_contained(input_log, x, y))

	#log = timestamp_filter.filter_traces_contained(input_log, custom_time_range[0][0], custom_time_range[0][1])
	log = pm4py.objects.log.log.EventLog()
	for timeslice in logs:
		for trace in timeslice:
			log.append(trace)
	print(len(input_log))
	print(len(log))
	print(type(log))
	#l2
	not_filtered_logs = {}
	not_filtered_logs["timestamp_filter"] = pm4py.objects.log.log.EventLog()
	for trace in input_log:
		if trace not in log:
			not_filtered_logs["timestamp_filter"].append(trace)
	print(len(not_filtered_logs["timestamp_filter"]))

	time_variants_started = datetime.now() # where should I start?

	variants = variants_filter.get_variants(log)
	from pm4py.statistics.traces.log import case_statistics
	variants_count = case_statistics.get_variant_statistics(log)
	variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=False)

	custom_path_range = sorted(custom_path_range, reverse=False)
	# check overlapping
	for i in range(0,len(custom_path_range)-1):
		if(custom_path_range[i][1] > custom_path_range[i+1][0]):
			print("THROW EXCEPTION: Overlapping range")

	nr_variants = len(variants_count)
	custom_path_range * nr_variants
	idx = [(round(x*nr_variants), round(y*nr_variants)) for (x,y) in custom_path_range]
	flatten = lambda l: [item for sublist in l for item in sublist]
	variants_subset = [variants_count[x:y+1] for (x,y) in idx]
	variants_subset = flatten(variants_subset)
	filtered_variants = {k:v for k,v in variants.items() if k in [x["variant"] for x in variants_subset]}
	#l2
	not_filtered_variants = {k:v for k,v in variants.items() if k not in [x["variant"] for x in variants_subset]}

	filtered_log = variants_filter.apply(log, filtered_variants)
	#l2
	not_filtered_logs["variant_filter"] = variants_filter.apply(log, not_filtered_variants)


	time_variants_finished = datetime.now() # note: incl log2 generation

	variants = variants_filter.get_variants(filtered_log)
	variants_count = case_statistics.get_variant_statistics(filtered_log)
	variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=False)

	activities = dict()
	for variant in variants_count:
		for activity in variant["variant"].split(","):
			if (activity not in activities.keys()):
				activities[activity] = variant["count"]
			else:
				activities[activity] += variant["count"]

	sorted_activities = {k: v for k, v in sorted(activities.items(), key=lambda item: item[1])}
	activities_sorted_list = list(sorted_activities)
	custom_activitiy_range = sorted(custom_activitiy_range, reverse=False)
	# check overlapping
	for i in range(0,len(custom_activitiy_range)-1):
		if(custom_activitiy_range[i][1] > custom_activitiy_range[i+1][0]):
			print("THROW EXCEPTION: Overlapping range")
	nr_activities = len(activities_sorted_list)
	idx = [(round(x*nr_activities), round(y*nr_activities)) for (x,y) in custom_activitiy_range]
	activities_to_keep = [activities_sorted_list[x:y+1] for (x,y) in idx]
	activities_to_keep = flatten(activities_to_keep)
	variants_idx = []
	for i in range(len(variants_count)):
		for activity in activities_to_keep:
			if (activity in variants_count[i]["variant"].split(",") and (i not in variants_idx)):
				variants_idx.append(i)
	variants_subset = [variants_count[i] for i in variants_idx]
	filtered_variants = {k:v for k,v in variants.items() if k in [x["variant"] for x in variants_subset]}
	#l2
	not_filtered_variants = {k:v for k,v in variants.items() if k not in [x["variant"] for x in variants_subset]}

	filtered_log = variants_filter.apply(filtered_log, filtered_variants)

	#l2
	not_filtered_logs["activities_filter_variants"] = variants_filter.apply(filtered_log, not_filtered_variants)

	new_log = pm4py.objects.log.log.EventLog()
	not_filtered_logs["activities_filter_traces"] = pm4py.objects.log.log.EventLog()
	for trace in filtered_log:
		new_trace = pm4py.objects.log.log.Trace()
		not_new_trace = pm4py.objects.log.log.Trace()
		for event in trace:
			if(event['concept:name'] in activities_to_keep):
				new_trace.append(event)
			else:
				not_new_trace.append(event)
		if(len(new_trace)>0):
			new_log.append(new_trace)
		if(len(not_new_trace)>0):
			not_filtered_logs["activities_filter_traces"].append(not_new_trace)

	#construct the filtered_out_log
	#filtered_out_log = pm4py.objects.log.log.EventLog()
	#for trace in log:

	time_activities_finished = datetime.now()

	from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
	heu_net = heuristics_miner.apply_heu(new_log, parameters={"dependency_thresh": 0.99})
	from pm4py.visualization.heuristics_net import visualizer as hn_vis_factory
	gviz = hn_vis_factory.apply(heu_net)
	hn_vis_factory.view(gviz)
	#subprocess.call(["rm", "-f", req.session["id"] + "_l1*"])
	hn_vis_factory.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l1.png"))
	#print("Saved l1 model as " + req.session["id"] + "_l1.xes")
	from pm4py.objects.log.exporter.xes import exporter as xes_exporter
	xes_exporter.apply(new_log, os.path.join("webapp","static", req.session["id"] + "_l1.xes"))


	#l2
	not_filtered_log = pm4py.objects.log.log.EventLog()
	for part in not_filtered_logs.keys():
		for trace in not_filtered_logs[part]:
			not_filtered_log.append(trace)
	heu_net = heuristics_miner.apply_heu(not_filtered_log, parameters={"dependency_thresh": 0.99})
	gviz = hn_vis_factory.apply(heu_net)
	hn_vis_factory.view(gviz)
	hn_vis_factory.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l2.png"))
	xes_exporter.apply(not_filtered_log, os.path.join("webapp","static", req.session["id"] + "_l2.xes"))

	used_paths = 0
	for lower, higher in custom_path_range:
		used_paths += round((higher-lower)*100)
	print(f"Using {used_paths}% of paths. {100-used_paths}% of paths are discarded.")

	print("Timestamp filter: {} seconds. \nVariants filter: {} seconds. \nActivities filter: {} seconds.".format((time_variants_started - time_timestamp_started).total_seconds(), (time_variants_finished - time_variants_started).total_seconds(), (time_activities_finished - time_variants_finished).total_seconds()))
	response = HttpResponse(json.dumps({'time':(time_variants_started - time_timestamp_started).total_seconds(), 'variants':(time_variants_finished - time_variants_started).total_seconds(), 'activities':(time_activities_finished - time_variants_finished).total_seconds()}))
	response.status_code = 200
	return response

