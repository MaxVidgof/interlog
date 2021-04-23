import Component from './Component.js';
import { v4 as uuidv4 } from 'https://jspm.dev/uuid';
 
export default class Slider extends Component {
	constructor(onDeletePressed, onChange, type, start, end) {
		super();
		this.type = type
//		this.div = document.createElement('div');
		this.id = Date.now().toString()+uuidv4();
		this.root.setAttribute('id', this.id);
		this.root.setAttribute('class','form-group')
//		this.root.appendChild(this.div);
		this.onChange = onChange
		this.deleteBtn = document.createElement('button');
		this.deleteBtn.innerText = '-';
		this.deleteBtn.addEventListener('click', () => {onDeletePressed(this);});
		this.root.appendChild(this.deleteBtn);
//		if (type==="datetime-local" && start !== undefined && end !== undefined){
			this.min = start;
			this.max = end;
//		} else {
//			this.min = 0;
//			this.max = 1;
//		}
		this.leftInput = document.createElement('input');
		this.createField(this.leftInput, 'left');
		this.rightInput = document.createElement('input');
		this.createField(this.rightInput, 'right');
		this.root.appendChild(document.createElement('br'));
		this.leftSlider = document.createElement('input');
		this.createSlider(this.leftSlider, 'left');
		this.rightSlider = document.createElement('input');
		this.createSlider(this.rightSlider, 'right');
		// slider
		this.left = this.leftInput.min;
		this.right = this.rightInput.max;
		this.leftInput.addEventListener('change', (evt) => {this.left = this.leftInput.value});
		this.rightInput.addEventListener('change', (evt) => this.right = this.rightInput.value);
		this.leftSlider.addEventListener('change', (evt) => this.left =this.leftSlider.value);
		this.rightSlider.addEventListener('change', (evt) => this.right = this.rightSlider.value);

	}
 
	set left(val) {
		if (this.type=='datetime-local') {
			if (!isNaN(val)) {
				this.leftInput.value = (new Date((new Date(this.min+"Z")).getTime()+(this.leftSlider.value * 1))).toISOString().split("Z")[0].split(".")[0].replace("T", " ");
				this.leftSlider.value = val;
			} else {
				this.leftInput.value = val;
				this.leftSlider.value = (new Date(val+"Z")) - (new Date(this.min));
			}
		} else {
			if((val >= this.min ) && (val <=this. max)){
				this.leftInput.value = val;
				this.leftSlider.value = val;
			} else {
				this.leftInput.value = this.min;
				this.leftSlider.value = this.min;
			}
		}
//		this.left = val;
		this.onChange()
		// slider
	}
 
	set right(val) {
		if (this.type=='datetime-local') {
			if(!isNaN(val)) {
				this.rightInput.value = (new Date((new Date(this.min+"Z")).getTime()+(this.rightSlider.value * 1))).toISOString().split("Z")[0].split(".")[0].replace("T", " ");
				this.rightSlider.value = val;
			} else {
				this.rightInput.value = val;
				this.rightSlider.value = (new Date(val+"Z")) - (new Date(this.min));
			}
		} else {
			if((val >=this.min ) && (val <= this.max)){
				this.rightInput.value = val;
				this.rightSlider.value = val;
			} else {
				this.rightInput.value = this.max;
				this.rightSlider.value = this.max;
			}
		}

		this.onChange()
//		this.right = val;
		// slider
	}
	set lower (val) {
		this.min = val;
		this.leftInput.min = val;
		this.leftSlider.min = val;
		this.rightInput.min = val;
		this.rightSlider.min = val;
		this.left = this.min;
		this.right = this.max;
	}

	set upper (val) {
		this.max = val;
		this.leftInput.max = val;
		this.leftSlider.max = val;
		this.rightInput.max = val;
		this.rightSlider.max = val;
		this.left = this.min;
		this.right = this.max;
	}

	createField(field, side){
		field.required=true;
		field.min = this.min;
		field.max = this.max;

		if (this.type==="number") {
			field.type = "number";
			field.step = 0.01;
		} else if (this.type==="datetime-local") {
			field.type = "text" //"datetime-local"
			field.setAttribute('class', "datetimeInput");
			field.setAttribute('id', `${this.id}_${side}`);
		}
		field.value = (side==="left" ? field.min : field.max);
		this.root.appendChild(field);
	}
	createSlider(field, side) {
		field.type = "range";
		field.min = 0;
		if (this.type==="number"){
			field.max = 1;
			field.step = 0.05;
			field.value = eval("this."+side+"Input.value");
		} else if (this.type==="datetime-local"){
			field.max = (new Date(this.max+"Z")) - (new Date(this.min+"Z"))
			field.step = (field.max - field.min)/50
			field.value = (new Date(eval("this."+side+"Input.value"))) - (new Date(this.min+"Z"))
		}
		this.root.appendChild(field);
	}
	render(parent) {
		super.render(parent)
		if(this.type==="datetime-local") {
			AnyTime.noPicker(`${this.id}_left`)
			AnyTime.picker( `${this.id}_left`, { format: "%Y-%m-%d %H:%i:%s", firstDOW: 1 } );
			AnyTime.noPicker(`${this.id}_right`)
			AnyTime.picker( `${this.id}_right`, { format: "%Y-%m-%d %H:%i:%s", firstDOW: 1 } ); //%: for timezone
		}
	}

}
