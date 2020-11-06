import Component from './Component.js';
import Slider from './Slider.js';

export default class Filter extends Component{
	constructor(onChange, filterName, type, start, end){
		super();
		this.root.setAttribute('class', 'filter')
		this.header = document.createElement("h3");
		this.header.innerText = filterName;
		this.sliders = [];
		this.sliders = [new Slider(this.onDeletePressed.bind(this), () => {
			onChange(this.intervals);
			//console.log(this);
		}, type, start, end)]
		this.sliders[0].leftInput.value = this.sliders[0].leftInput.min
		this.sliders[0].rightInput.value = this.sliders[0].rightInput.max

		this.addBtn = document.createElement("button");
		this.addBtn.innerText = "+";
		this.addBtn.addEventListener('click', () => {
			this.sliders.push(new Slider(this.onDeletePressed.bind(this), () => {onChange(this.intervals)}, type, start, end));
			this.sliders.forEach(slider => slider.render(this.root))
			this.sliders[this.sliders.length -1].leftInput.value = this.sliders[this.sliders.length - 2].rightInput.value
			this.sliders[this.sliders.length -1].rightInput.value = this.sliders[0].rightInput.max
			this.sliders[this.sliders.length -1].leftSlider.value = this.sliders[this.sliders.length - 2].rightSlider.value
		});
		this.root.appendChild(this.header)
		this.root.appendChild(this.addBtn)
		//this.sliders.forEach(slider => slider.render(this.root))
	}
	onDeletePressed(deletedSlider){
		this.sliders = this.sliders.filter((slider) => {
			return slider.id !== deletedSlider.id
		})
		//console.log(this.sliders.length)
		document.getElementById(deletedSlider.id).parentElement.remove();
		//this.root.removeChild(deletedSlider);
	}

	get intervals() {
		let vals = [];
		this.sliders.forEach((slider) => {vals.push([slider.leftInput.value, slider.rightInput.value])});
		return vals;
	}

	render(parent) {
		super.render(parent)
                this.sliders.forEach(slider => slider.render(this.root))
	}
}
