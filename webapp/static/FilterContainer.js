import Component from './Component.js';
import Filter from './Filter.js';

export default class FilterContainer extends Component{
	constructor(onApplyPushed, start, end){
		super()
		this.root.setAttribute('class', 'col-sm');
		this.onApplyPushed = onApplyPushed
		this.filterSettings = {
			filter1: [],
			filter2: [],
			filter3: []
		}
		this.filter1 = new Filter(this.setFilter1.bind(this), "Time filter", "datetime-local", start, end);
		this.filter2 = new Filter(this.setFilter2.bind(this), "Variants filter", "number");
		this.filter3 = new Filter(this.setFilter3.bind(this), "Activities filter", "number");

		this.applyBtn = document.createElement("button");
		this.applyBtn.innerText = "Apply";
		this.applyBtn.setAttribute('class', 'btn btn-primary')
		this.applyBtn.addEventListener('click', () => {
//			let data = new FormData();
//let filters = document.getElementsByClassName("filter");
//let filtersOk = true;
//for (filter of filters) {
//     for (let i = 2; i < filter.children.length; i = i+1)
//        if (!(filter.children[i].children[1].value <= filter.children[i].children[2].value)) {filtersOk = false}
//    for (i = 2; i < filter.children.length -1; i = i + 1){
//        if (!(filter.children[i].children[2].value <= filter.children[i+1].children[1].value)) {filtersOk = false}
//    }
//}
//if (filtersOk) {
let data = JSON.stringify(this.filterSettings)
//                data.append('input_log_file', input.files[0])
	                fetch("https://cherry-picker.cluster.ai.wu.ac.at/apply", {method: 'POST', body: data}).then((response => {return response.json()})).then((data) => {
//console.log(data)
				if (data.status && data.status==="expired"){ alert("Session expired. Please reload the page.");}
				console.log("Time filter: " + data.time + " seconds")
				console.log("Variants filter: " + data.variants + " seconds")
				console.log("Activities filter: " + data.activities + " seconds")
				onApplyPushed("applied");
			});
//			fetch().then(() => {onApplyPushed()});
//} else {
//	alert("Wrong filter settings!");
//}
console.log(this.filterSettings)
		})
//this.root.appendChild(this.filterX.render())
		//
		this.filters = document.createElement('div')
		this.root.appendChild(this.filters)
		this.root.appendChild(this.applyBtn)
	}

	setFilter1(intervals){
		this.filterSettings.filter1 = intervals
	}
	setFilter2(intervals){
		this.filterSettings.filter2 = intervals
	}
	setFilter3(intervals){
		this.filterSettings.filter3 = intervals
	}

	render(parent){
		super.render(parent)
		this.filter1.render(this.filters)
		this.filter2.render(this.filters)
		this.filter3.render(this.filters)
	}
}
