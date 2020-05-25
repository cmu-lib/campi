<template>
  <b-card class="my-2" header="Date digitized">
    <VueSlider
      v-model="digitized_date_range"
      tooltip="always"
      tooltip-placement="top"
      :enable-cross="false"
      :min="start_date"
      :max="end_date"
      @change="update_range()"
    />
  </b-card>
</template>

<script>
import VueSlider from "vue-slider-component";
import "vue-slider-component/theme/default.css";
import _ from "lodash";
export default {
  name: "DigitizedDate",
  components: { VueSlider },
  props: {
    value: Array,
    directory: null
  },
  data() {
    return {
      digitized_date_range: [],
      start_date: 2003,
      end_date: 2020
    };
  },
  watch: {
    // vue-slider does not come with a built-in debounce method so we must use lodash to keep from sending too many calls to the server
    digitized_date_range: _.debounce(function() {
      this.$emit("input", this.digitized_date_range);
    }, 1000),
    value() {
      this.digitized_date_range = this.value;
    }
  },
  mounted() {
    this.digitized_date_range = this.value;
  }
};
</script>