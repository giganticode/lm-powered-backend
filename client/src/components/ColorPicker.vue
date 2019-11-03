<template>
  <div class="color-picker uk-inline " ref="colorpicker">
	<span class="uk-form-icon">
		<span class="current-color" :style="'background-color: ' + colorValue" @click="togglePicker()"></span>
	</span>
    <chrome-picker :value="color" @input="updateFromPicker" v-if="displayPicker" />
	<input type="text" readonly class="uk-input" v-model="colorValue" @focus="showPicker()" @input="updateFromInput" />
</div>
</template>

<script>
export default {
    props: {
        color: {
            default: "#000000",
            type: String
        },
	},
	watch: {
		colorValue(val) {
			if (val) {
				this.updateColors(val);
				this.$emit('input', val);
			}
		},
		color: function(newVal, oldVal) { // watch prop color set from outside when color mapping is reset
			this.setColor(newVal);
		},
	},
	data() {
		return {
			colorValue: '',
			displayPicker: false,
		}
	},
	mounted() {
		this.setColor(this.color || '#000000');
	},
	methods: {
		setColor(color) {
			this.updateColors(color);
			this.colorValue = color;
		},
		updateColors(color) {
			if(color.slice(0, 1) == '#') {
				this.colors = {
					hex: color
				};
			}
			else if(color.slice(0, 4) == 'rgba') {
				var rgba = color.replace(/^rgba?\(|\s+|\)$/g,'').split(','),
					hex = '#' + ((1 << 24) + (parseInt(rgba[0]) << 16) + (parseInt(rgba[1]) << 8) + parseInt(rgba[2])).toString(16).slice(1);
				this.colors = {
					hex: hex,
					a: rgba[3],
				}
			}
		},
		showPicker() {
			document.addEventListener('click', this.documentClick);
			this.displayPicker = true;
		},
		hidePicker() {
			document.removeEventListener('click', this.documentClick);
			this.displayPicker = false;
		},
		togglePicker() {
			this.displayPicker ? this.hidePicker() : this.showPicker();
		},
		updateFromInput() {
			this.updateColors(this.colorValue);
		},
		updateFromPicker(color) {
			this.colors = color;
			if(color.rgba.a == 1) {
				this.colorValue = color.hex;
			}
			else {
				this.colorValue = 'rgba(' + color.rgba.r + ', ' + color.rgba.g + ', ' + color.rgba.b + ', ' + color.rgba.a + ')';
			}
		},
		documentClick(e) {
			var el = this.$refs.colorpicker, target = e.target;
			if(!el || (el !== target && !el.contains(target))) {
				this.hidePicker()
			}
		}
	},
}
</script>

<style scoped>
.color-picker input {
    min-width: 190px;
}
.vc-chrome {
	position: absolute;
	top: 35px;
	right: 0;
	z-index: 9;
}
.current-color {
	display: inline-block;
	width: 16px;
	height: 16px;
	background-color: #000;
	cursor: pointer;
}
.footer {
	margin-top: 20px;
	text-align: center;
}
.color-picker {
    position: relative;
}
</style>
