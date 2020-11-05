import Component from './Component.js';
import Filter from './Filter.js';

export default class FilterContainer extends Component{
	constructor(onApplyPushed){
		super()
		this.onApplyPushed = onApplyPushed
		this.filterSettings = {
			filter1: [],
			filter2: [],
			filter3: []
		}
		this.filter1 = new Filter(this.setFilter1.bind(this), "Time filter", "datetime-local");
		this.filter2 = new Filter(this.setFilter2.bind(this), "Variants filter", "number");
		this.filter3 = new Filter(this.setFilter3.bind(this), "Activities filter", "number");

		this.applyBtn = document.createElement("button");
		this.applyBtn.innerText = "APPLY";
		this.applyBtn.addEventListener('click', () => {
//			let data = new FormData();
let data = JSON.stringify(this.filterSettings)
//                data.append('input_log_file', input.files[0])
	                fetch("http://10.139.167.139:8000/apply", {method: 'POST', body: data}).then((response => {return response.json()})).then((data) => {
//console.log(data)
				console.log("Time filter: " + data.time + " seconds")
				console.log("Variants filter: " + data.variants + " seconds")
				console.log("Activities filter: " + data.activities + " seconds")
				onApplyPushed("applied");
			});
//			fetch().then(() => {onApplyPushed()});

console.log(this.filterSettings)
		})
		this.root.appendChild(this.filter1.render())
		this.root.appendChild(this.filter2.render())
		this.root.appendChild(this.filter3.render())
		//
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

//	render(parent){
//		return super.render(parent)
//	}
}
