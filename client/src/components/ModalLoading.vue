<template>
  <div ref="modal" class="loading uk-flex-top" uk-modal="esc-close:true;bg-close:false;stack:true">
    <div class="uk-modal-dialog uk-modal-body uk-margin-auto-vertical">
      <div class="uk-flex uk-flex-middle uk-flex-center uk-width-1-1 uk-height-1-1">
        <div uk-spinner="ratio: 3"></div>
      </div>
      <p class="uk-text-center">
        <button class="uk-button uk-button-default" @click="cancel" type="button">Cancel</button>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      modal: null
    };
  },
  beforeDestroy() {
    if (this.modal !== null) {
      this.modal.$destroy(true);
    }
  },
  methods: {
    show() {
	  if (this.modal === null) {
	  	this.modal = UIkit.modal(this.$refs.modal);
    }
    this.modal.show();
    },
    hide() {
      this.modal.hide();
	  },
    cancel() {
      this.$emit('cancel')
    },
  }
};
</script>

<style>

</style>
