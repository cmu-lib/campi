<template>
  <div class="m-3">
    <b-img :src="photograph.image.square" :class="{'approved': approved}" />
    <div class="photo-square-buttons">
      <b-button class="mx-2" variant="success" size="sm" @click="toggle_photo" :pressed="approved">
        <BIconCheck2 />
      </b-button>
      <b-button class="mx-2" variant="info" size="sm" @click="get_info">
        <BIconInfoCircleFill />
      </b-button>
    </div>
  </div>
</template>

<script>
import { BIconCheck2, BIconInfoCircleFill } from "bootstrap-vue";
export default {
  name: "PhotoSquare",
  components: { BIconCheck2, BIconInfoCircleFill },
  props: {
    photograph: {
      type: Object,
      required: true
    },
    approved: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggle_photo() {
      this.$emit("toggle_photo", this.photograph);
    },
    get_info() {
      this.$emit("get_info", this.photograph);
    }
  }
};
</script>

<style>
img.approved {
  outline: 3px solid orange;
}

.button-image-container {
  position: relative;
}

/* .photo-square-buttons {
  position: absolute;
  top: 80%;
  left: 50%;
  transform: translate(-50%, -50%);
  -ms-transform: translate(-50%, -50%);
} */
</style>