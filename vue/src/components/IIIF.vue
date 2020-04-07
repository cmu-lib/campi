<template>
  <div :id="id" class="osd"></div>
</template>

<script>
import OpenSeadragon from "openseadragon";
export default {
  name: "IIIF",
  props: {
    id: {
      type: String,
      default: "iiif"
    },
    info_url: String
  },
  data() {
    return {};
  },
  computed: {
    options() {
      return {
        id: this.id,
        prefixUrl: "/osd/",
        tileSources: this.info_url,
        showRotationControl: true,
        gestureSettingsTouch: {
          pinchRotate: true
        }
      };
    }
  },
  mounted() {
    OpenSeadragon(this.options);
  }
};
</script>

<style>
.osd:not(:fullscreen) {
  position: relative;
  height: 800px;
  width: 100%;
  border-top: 1px lightgray solid;
  border-bottom: 1px lightgray solid;
}
</style>