from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime, timedelta
import hashlib
import subprocess
from django.http import HttpResponse
import os
import pm4py
import json
import dateutil.parser
from django.core.serializers.json import DjangoJSONEncoder
import glob
import math
from .lev import levenshteinDistanceDP as lev_dist
#from celery import Celery
#from celery.schedules import crontab
#pm4py imports
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.heuristics_net import visualizer as hn_vis_factory
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.filtering.log.timestamp import timestamp_filter
from pm4py.statistics.traces.log import case_statistics
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization

#TODO: users map for garbage collection
sessions = {}

def index(req):
	req.session["id"] = hashlib.sha256(bytes(str(req.META["REMOTE_ADDR"]) + str(datetime.now()), 'utf-8')).hexdigest()
	req.session.set_expiry(7200)
	delete_old_files()
	return render(req, "index.html", {"baseUrl": req.session["id"]})

def check_session_id_or_redirect(func):
	def inner(req):
		print(req.session)
		req.session.clear_expired()
		print(req.session)
		if not req.session.get("id", None):
			return HttpResponse(json.dumps({"status":"expired"}))
		return func(req)
	return inner

@check_session_id_or_redirect
def upload_log(req):
	input_log_file = req.FILES["input_log_file"]
	sessions[req.session["id"]] = datetime.now()
	req.session.set_expiry(7200) #7200 = 2hrs
	subprocess.call(["rm", "-f", req.session["id"] + "_*"])
	with open(os.path.join("webapp","static", req.session["id"] + "_l0.xes"), 'wb') as file:
		file.write(input_log_file.read())
	input_file = os.path.join("webapp","static", req.session["id"] + "_l0.xes")
	log = xes_importer.apply(input_file)
	heu_net = heuristics_miner.apply_heu(log, parameters={"dependency_thresh": 0.99})
	gviz = hn_vis_factory.apply(heu_net)
	hn_vis_factory.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l0.png"))
	#Find minimum and maximum timestamps
	start_time = min([event["time:timestamp"] for trace in log for event in trace])
	start_times_a = [event["start_timestamp"] for trace in log for event in trace if "start_timestamp" in event.keys()]
	if len(start_times_a)>0:
		start_time = min(start_time, min(start_times_a))
	end_time = max([event["time:timestamp"] for trace in log for event in trace]) + timedelta(seconds=1)
	flatten = lambda l: [item for sublist in l for item in sublist]
	trace_attributes = list(set(flatten([trace.attributes.keys() for trace in log])).difference(['concept:name']))

	trace_attributes = [{'name':attribute, 'level':'trace'} for attribute in trace_attributes]
	for i in range(len(trace_attributes)):
		trace_attributes[i]['min'] = min([trace.attributes[trace_attributes[i]['name']] for trace in log if trace_attributes[i]['name'] in trace.attributes.keys()])
		trace_attributes[i]['max'] = max([trace.attributes[trace_attributes[i]['name']] for trace in log if trace_attributes[i]['name'] in trace.attributes.keys()])
		trace_attributes[i]['type'] = type(trace_attributes[i]['min']).__name__
		if trace_attributes[i]['type']=='str':
			trace_attributes[i]['min']=0
			trace_attributes[i]['max']=1

	trace_attributes = [attribute for attribute in trace_attributes if attribute['type'] != 'bool']

	event_attributes = list(set(flatten([event.keys() for trace in log for event in trace])).difference(['concept:name', 'time:timestamp']))
	event_attributes = [{'name':attribute, 'level':'event'} for attribute in event_attributes]
	for i in range(len(event_attributes)):
		event_attributes[i]['min'] = min([event[event_attributes[i]['name']] for trace in log for event in trace if event_attributes[i]['name'] in event.keys()])
		event_attributes[i]['max'] = max([event[event_attributes[i]['name']] for trace in log for event in trace if event_attributes[i]['name'] in event.keys()])
		event_attributes[i]['type'] = type(event_attributes[i]['min']).__name__
		if event_attributes[i]['type']=='str':
			event_attributes[i]['min']=0
			event_attributes[i]['max']=1

	event_attributes = [attribute for attribute in event_attributes if attribute['type'] != 'bool']

	print(trace_attributes)
	print(event_attributes)
	response = HttpResponse(json.dumps({'start_time': start_time, 'end_time': end_time, 'traces_u':len(log), 'trace_attributes':trace_attributes, 'event_attributes':event_attributes}, sort_keys=True, indent=1, cls=DjangoJSONEncoder))
	response.status_code = 200
	return response

@check_session_id_or_redirect
def apply_filter(req):
	sessions[req.session["id"]] = datetime.now()
	filters = {
		"time": True,
		"variants": True,
		"performance": True,
		"activities": True,
		"attribute": True
	}
	req.session.set_expiry(7200)
	#print(str(req.body))
	o = json.loads(req.body)
	print(str(o))
	custom_time_range = []
	for pair in o["filter1"]:
		#custom_time_range.append((dateutil.parser.parse(pair[0]),dateutil.parser.parse(pair[1])))
		custom_time_range.append((pair[0],pair[1]))
	if o["filter1"] == []:
		filters["time"] = False
	#print(o["filter1"][0])
	#print(custom_time_range[0][0])
	#print(custom_time_range)
	custom_path_range = []
	for pair in o["filter2"]:
		custom_path_range.append((float(pair[0]),float(pair[1])))
	if o["filter2"] == []:
		filters["variants"] = False
		#custom_path_range = [(0,1)] #filter2
	custom_performance_range = []
	for pair in o["filter3"]:
		custom_performance_range.append((float(pair[0]),float(pair[1])))
	if o["filter3"] == []:
		filters["performance"] = False
	custom_activitiy_range = []
	for pair in o["filter4"]:
		custom_activitiy_range.append((float(pair[0]),float(pair[1])))
	if o["filter4"] == []:
		filters["activities"] = False
		#custom_activitiy_range = [(0,1)] #filter3
	custom_attribute_range = []
	for pair in o["filter5"]:
		custom_attribute_range.append((float(pair[0]),float(pair[1])))
	if o["filter5"] == [] or o["filter5attribute"] == "Empty":
		filters["attribute"] = False
	additional_attribute = o["filter5attribute"]

	selected_viz = o["visualization"]
	calc_lev = o["distance"]
	input_file = os.path.join("webapp","static", req.session["id"] + "_l0.xes")
	input_log = xes_importer.apply(input_file)
	not_filtered_logs = {}
	flatten = lambda l: [item for sublist in l for item in sublist]

	time_timestamp_started = datetime.now()
	if filters["time"]:
		#TODO check overlapping for filter
		custom_time_range = sorted(custom_time_range, reverse=False)
		for i in range(0,len(custom_time_range)-1):
			if(custom_time_range[i][1] > custom_time_range[i+1][0]):
				response = HttpResponse(json.dumps({'error': "Wrong intervals for time filter"}))
				response.status_code = 200
				return response
				#raise ValueError("Overlapping time ranges")

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
		#l2
		not_filtered_logs["timestamp_filter"] = pm4py.objects.log.log.EventLog()
		for trace in input_log:
			if trace not in log:
				not_filtered_logs["timestamp_filter"].append(trace)
		print(len(not_filtered_logs["timestamp_filter"]))
	else:
		log = input_log

	time_variants_started = datetime.now() # where should I start?

	if filters["variants"]:
		variants = variants_filter.get_variants(log)
		variants_count = case_statistics.get_variant_statistics(log)
		variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=False)

		custom_path_range = sorted(custom_path_range, reverse=False)
		# check overlapping
		for i in range(0,len(custom_path_range)-1):
			if(custom_path_range[i][1] > custom_path_range[i+1][0]):
				response = HttpResponse(json.dumps({'error': "Wrong intervals for variants filter"}))
				response.status_code = 200
				return response
				#raise ValueError("Overlapping variants ranges")

		nr_variants = len(variants_count)
		custom_path_range * nr_variants
		idx = [(math.floor(x*nr_variants), math.ceil(y*nr_variants)) for (x,y) in custom_path_range]
		variants_subset = [variants_count[x:y+1] for (x,y) in idx]
		variants_subset = flatten(variants_subset)
		filtered_variants = {k:v for k,v in variants.items() if k in [x["variant"] for x in variants_subset]}
		#l2
		not_filtered_variants = {k:v for k,v in variants.items() if k not in [x["variant"] for x in variants_subset]}

		filtered_log = variants_filter.apply(log, filtered_variants)
		#l2
		not_filtered_logs["variant_filter"] = variants_filter.apply(log, not_filtered_variants)
	else:
		filtered_log = log

	time_variants_finished = datetime.now() # note: incl log2 generation

	if filters["performance"]:
		custom_performance_range = sorted(custom_performance_range, reverse=False)
		# check overlapping
		for i in range(0,len(custom_performance_range)-1):
			if(custom_performance_range[i][1] > custom_performance_range[i+1][0]):
				response = HttpResponse(json.dumps({'error': "Wrong intervals for performance filter"}))
				response.status_code = 200
				return response
				#raise ValueError("Overlapping performance ranges")

		#all_case_durations = case_statistics.get_all_casedurations(log, parameters={case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})
		#case_filter.filter_case_performance(log, 86400, 864000)
		performances = []
		for i in range(len(filtered_log)):
			filtered_log[i].attributes["throughput"] = (max([event["time:timestamp"]for event in filtered_log[i]])-min([event["time:timestamp"] for event in filtered_log[i]])).total_seconds()
			performances.append(filtered_log[i].attributes["throughput"])

		nr_cases = len(filtered_log)
		performances = sorted(performances, reverse=False)
		idx = [(math.floor(x*nr_cases), math.ceil(y*nr_cases)) for (x,y) in custom_performance_range]
		perf_subset = [performances[x:y+1] for (x,y) in idx]
		perf_subset = flatten(perf_subset)

		performance_log = pm4py.objects.log.log.EventLog([trace for trace in filtered_log if trace.attributes["throughput"] in perf_subset])
		#l2
		not_filtered_logs["performance_filter"] = pm4py.objects.log.log.EventLog([trace for trace in filtered_log if trace.attributes["throughput"] not in perf_subset])
		#print(str(len(not_filtered_logs["performance_filter"])))

	else:
		performance_log = filtered_log

	time_performance_finished = datetime.now()

	if filters["activities"]:
		variants = variants_filter.get_variants(performance_log)
		variants_count = case_statistics.get_variant_statistics(performance_log)
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
				response = HttpResponse(json.dumps({'error': "Wrong intervals for activities filter"}))
				response.status_code = 200
				return response
				#raise ValueError("Overlapping activities ranges")
		nr_activities = len(activities_sorted_list)
		idx = [(math.floor(x*nr_activities), math.ceil(y*nr_activities)) for (x,y) in custom_activitiy_range]
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

		filtered_log = variants_filter.apply(performance_log, filtered_variants)

		#l2
		not_filtered_logs["activities_filter"] = variants_filter.apply(performance_log, not_filtered_variants)

		new_log = pm4py.objects.log.log.EventLog()
		#not_filtered_logs["activities_filter_traces"] = pm4py.objects.log.log.EventLog()
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
				not_filtered_logs["activities_filter"].append(not_new_trace)
	else:
		new_log = performance_log

	time_activities_finished = datetime.now()

	if filters["attribute"]:
		custom_attribute_range = sorted(custom_attribute_range, reverse=False)
		# check overlapping
		for i in range(0,len(custom_attribute_range)-1):
			if(custom_attribute_range[i][1] > custom_attribute_range[i+1][0]):
				response = HttpResponse(json.dumps({'error': "Wrong intervals for additional attribute filter"}))
				response.status_code = 200
				return response

		newest_log = pm4py.objects.log.log.EventLog()
		not_filtered_logs["additional_filter"] = pm4py.objects.log.log.EventLog()

		traces_with_attr = []
		not_traces_with_attr = []
		for trace in new_log:
			if additional_attribute in trace.attributes.keys():
				traces_with_attr.append(trace)
			else:
				not_traces_with_attr.append(trace)
		#check if trace attribute
		if len(traces_with_attr)>0:
			#check if numeric
			if type(traces_with_attr[0].attributes[additional_attribute]) in [int, float]:
				for trace in traces_with_attr:
					if any([trace.attributes[additional_attribute] >= x and trace.attributes[additional_attribute] <= y for (x,y) in custom_attribute_range]):
						newest_log.append(trace)
					else:
						not_filtered_logs["additional_filter"].append(trace)
				for trace in not_traces_with_attr:
					not_filtered_logs["additional_filter"].append(trace)
			else: #string
				attribute_frequencies = dict()
				for trace in traces_with_attr:
					if additional_attribute not in attribute_frequencies.keys():
						attribute_frequencies[trace.attributes[additional_attribute]] = 0
					attribute_frequencies[trace.attributes[additional_attribute]] += 1

				sorted_frequencies = {k: v for k, v in sorted(attribute_frequencies.items(), key=lambda item: item[1])}
				frequencies_sorted_list = list(sorted_frequencies)

				nr_values = len(frequencies_sorted_list)
				idx = [(math.floor(x*nr_values), math.ceil(y*nr_values)) for (x,y) in custom_attribute_range]
				values_to_keep = [frequencies_sorted_list[x:y+1] for (x,y) in idx]
				values_to_keep = flatten(values_to_keep)

				for trace in traces_with_attr:
					if trace.attributes[additional_attribute] in values_to_keep:
						newest_log.append(trace)
					else:
						not_filtered_logs["additional_filter"].append(trace)
				for trace in not_traces_with_attr:
					not_filtered_logs["additional_filter"].append(trace)

		else: #event attribute
			if [type(event[additional_attribute]) for trace in new_log for event in trace if additional_attribute in event.keys()][0] in [int, float]:
				for trace in new_log:
					new_trace = pm4py.objects.log.log.Trace()
					not_new_trace = pm4py.objects.log.log.Trace()
					for event in trace:
						if(additional_attribute in event.keys() and any([event[additional_attribute] >= x and event[additional_attribute] <= y for (x,y) in custom_attribute_range ])):
							new_trace.append(event)
						else:
							not_new_trace.append(event)
					if(len(new_trace)>0):
						newest_log.append(new_trace)
					if(len(not_new_trace)>0):
						not_filtered_logs["additional_filter"].append(not_new_trace)
			else: #string
				attribute_frequencies = dict()
				for trace in new_log:
					for event in trace:
						if additional_attribute in event.keys():
							if additional_attribute not in attribute_frequencies.keys():
								attribute_frequencies[event[additional_attribute]] = 0
							attribute_frequencies[event[additional_attribute]] += 1

				sorted_frequencies = {k: v for k, v in sorted(attribute_frequencies.items(), key=lambda item: item[1])}
				frequencies_sorted_list = list(sorted_frequencies)

				nr_values = len(frequencies_sorted_list)
				idx = [(math.floor(x*nr_values), math.ceil(y*nr_values)) for (x,y) in custom_attribute_range]
				values_to_keep = [frequencies_sorted_list[x:y+1] for (x,y) in idx]
				values_to_keep = flatten(values_to_keep)

				for trace in new_log:
					new_trace = pm4py.objects.log.log.Trace()
					not_new_trace = pm4py.objects.log.log.Trace()
					for event in trace:
						if(additional_attribute in event.keys() and event[additional_attribute] in values_to_keep):
							new_trace.append(event)
						else:
							not_new_trace.append(event)
					if(len(new_trace)>0):
						newest_log.append(new_trace)
					if(len(not_new_trace)>0):
						not_filtered_logs["additional_filter"].append(not_new_trace)


	else:
		newest_log = new_log

	time_attribute_finished = datetime.now()

	if(selected_viz=="dfgf"):
		dfg = dfg_discovery.apply(newest_log)
		gviz = dfg_visualization.apply(dfg, log=newest_log, variant=dfg_visualization.Variants.FREQUENCY)
		dfg_visualization.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l1.png"))
	elif(selected_viz=="dfgp"):
		dfg = dfg_discovery.apply(newest_log)
		gviz = dfg_visualization.apply(dfg, log=newest_log, variant=dfg_visualization.Variants.PERFORMANCE)
		dfg_visualization.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l1.png"))
	else:
		heu_net = heuristics_miner.apply_heu(newest_log, parameters={"dependency_thresh": 0.99})
		gviz = hn_vis_factory.apply(heu_net)
		hn_vis_factory.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l1.png"))

	xes_exporter.apply(newest_log, os.path.join("webapp","static", req.session["id"] + "_l1.xes"))


	#l2
	not_filtered_log = pm4py.objects.log.log.EventLog()
	for part in not_filtered_logs.keys():
		for trace in not_filtered_logs[part]:
			not_filtered_log.append(trace)

	if(selected_viz=="dfgf"):
		dfg = dfg_discovery.apply(not_filtered_log)
		gviz = dfg_visualization.apply(dfg, log=not_filtered_log, variant=dfg_visualization.Variants.FREQUENCY)
		dfg_visualization.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l2.png"))
	elif(selected_viz=="dfgp"):
		dfg = dfg_discovery.apply(not_filtered_log)
		gviz = dfg_visualization.apply(dfg, log=not_filtered_log, variant=dfg_visualization.Variants.PERFORMANCE)
		dfg_visualization.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l2.png"))
	else:
		heu_net = heuristics_miner.apply_heu(not_filtered_log, parameters={"dependency_thresh": 0.99})
		gviz = hn_vis_factory.apply(heu_net)
		hn_vis_factory.save(gviz, os.path.join("webapp","static", req.session["id"] + "_l2.png"))
	xes_exporter.apply(not_filtered_log, os.path.join("webapp","static", req.session["id"] + "_l2.xes"))

	if(calc_lev):
		lev_new = [0]*len(newest_log)
		for i in range(len(newest_log)):
			lev_new[i] = [hash(event['concept:name']) for event in newest_log[i]]

		lev_not = [0]*len(not_filtered_log)
		for i in range(len(not_filtered_log)):
			lev_not[i] = [hash(event['concept:name']) for event in not_filtered_log[i]]

		distances = []
		for i in range(len(lev_new)):
			for j in range(len(lev_not)):
				distances.append(lev_dist(lev_new[i], lev_not[j]))
		lev_d = sum(distances)/len(distances)
		print("Levenshtein's distance: "+str(lev_d))
	else:
		lev_d = "null"

	used_paths = 0
	for lower, higher in custom_path_range:
		used_paths += round((higher-lower)*100)
	print(f"Using {used_paths}% of paths. {100-used_paths}% of paths are discarded.")

	print("Timestamp filter: {} seconds. \nVariants filter: {} seconds. \nPerformance filter: {} seconds. \nActivities filter: {} seconds. \nAttribute filter: {} seconds.".format((time_variants_started - time_timestamp_started).total_seconds(), (time_variants_finished - time_variants_started).total_seconds(), (time_performance_finished - time_variants_finished).total_seconds(), (time_activities_finished - time_performance_finished).total_seconds(), (time_attribute_finished - time_activities_finished).total_seconds()))
	response = HttpResponse(json.dumps({'time':(time_variants_started - time_timestamp_started).total_seconds(), 'variants':(time_variants_finished - time_variants_started).total_seconds(),'performance':(time_performance_finished - time_variants_finished).total_seconds(), 'activities':(time_activities_finished - time_performance_finished).total_seconds(), 'attribute':(time_attribute_finished - time_activities_finished).total_seconds(), 'traces':[len(newest_log), len(not_filtered_log)], 'distance':lev_d}))
	response.status_code = 200
	return response

#@periodic_task(run_every=crontab(minute='*/5'))
#app = Celery()

#@app.on_after_configure.connect
#def setup_periodic_tasks(sender, **kwargs):
#	sender.add_periodic_task(10, delete_old_files.s()) #minute=0, hour=*/2
#	sender.add_periodic_task(10,test.s())

#@app.task
def delete_old_files():
	#print(sessions.keys())
	del_list = []
	for user_id in sessions.keys() :
		# If the expiration date is bigger than now delete it
		if sessions[user_id] + timedelta(seconds=8000) < datetime.now(): #8000
			del_list.append(user_id)
	for element in del_list:
		print("deleting " + element)
		#subprocess.call(["ls", "-la"])
		files_to_delete = glob.glob(os.path.join("webapp", "static", element + "_*"))
		for file in files_to_delete:
			subprocess.call(["rm", "-f", file])
		del sessions[element]
	return "completed deleting file at {}".format(datetime.now())

