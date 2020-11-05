import Component from './Component.js';
import Slider from './Slider.js';

export default class Filter extends Component{
	constructor(onChange, filterName, type){
		super();
		this.header = document.createElement("h3");
		this.header.innerText = filterName;
		this.sliders = [];
		this.sliders = [new Slider(this.onDeletePressed.bind(this), () => {
			onChange(this.intervals);
			//console.log(this);
		}, type)]
		this.addBtn = document.createElement("button");
		this.addBtn.innerText = "+";
		this.addBtn.addEventListener('click', () => {
			this.sliders.push(new Slider(this.onDeletePressed.bind(this), () => {onChange(this.intervals)}, type));
			this.sliders.forEach(slider => slider.render(this.root))
		});
		this.root.appendChild(this.header)
		this.root.appendChild(this.addBtn)
		this.sliders.forEach(slider => slider.render(this.root))
	}

	onDeletePressed(deletedSlider){
		this.sliders.filter((slider) => {
			return slider.id !== deletedSlider.id
		})
		document.getElementById(deletedSlider.id).remove();
		//this.root.removeChild(deletedSlider);
	}

	get intervals() {
//console.log("here");
		let vals = [];
		this.sliders.forEach((slider) => {vals.push([slider.leftInput.value, slider.rightInput.value])});
		return vals;
	}
}
