<template>
  <b-container fluid>
    <div :id="div_id" class="osd">
      <div
        v-for="annotation in html_annotations"
        :key="annotation.id"
        :id="annotation.id"
        :class="annotation.class"
      >
        <span>{{ annotation.title }}</span>
      </div>
    </div>
  </b-container>
</template>

<script>
import OpenSeadragon from "openseadragon";
import _ from "lodash";
export default {
  name: "IIIF",
  props: {
    id: {
      type: Number,
      default: 1
    },
    annotations: Array,
    info_url: String
  },
  data() {
    return {};
  },
  computed: {
    div_id() {
      return `iiif-${this.id}`;
    },
    seadragon_annotations() {
      return this.annotations.map(a => _.omit(a, "title"));
    },
    html_annotations() {
      return this.annotations.map(a => {
        return {
          id: a.id,
          title: a.title,
          class: a.class
        };
      });
    },
    options() {
      return {
        id: this.div_id,
        prefixUrl: "/osd/",
        tileSources: this.info_url,
        showRotationControl: true,
        visibilityRatio: 0.2,
        gestureSettingsTouch: {
          pinchRotate: true
        },
        overlays: this.seadragon_annotations
      };
    }
  },
  mounted() {
    OpenSeadragon(this.options);
  }
};
</script>

<style lang="scss">
.osd:not(:fullscreen) {
  position: relative;
  height: 80vh;
  width: 100%;
  border-top: 1px lightgray solid;
  border-bottom: 1px lightgray solid;
}

.face-annotation {
  border: 2px solid orange;
  color: orange;
  span {
    background-color: seashell;
  }
}

.object-annotation {
  border: 2px solid skyblue;
  color: skyblue;
  span {
    background-color: seashell;
  }
}

.text-annotation {
  border: 2px solid greenyellow;
  color: greenyellow;
  span {
    background-color: seashell;
  }
}
</style>