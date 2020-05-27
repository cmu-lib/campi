<template>
  <b-card class="my-2">
    <b-button class="mx-1" v-if="!!directory" pill variant="primary" size="sm">
      <BIconFolderFill />
      <span class="mx-2">{{ directory.label }}</span>
      <BIconXCircle @click="$emit('clear_directory')" />
    </b-button>
    <b-button class="mx-1" v-if="!!job" pill variant="info" size="sm">
      <BIconCamera />
      <span class="mx-2">{{ job.label }}</span>
      <BIconXCircle @click="$emit('clear_job')" />
    </b-button>
    <b-button class="mx-1" v-if="show_range" pill variant="secondary" size="sm">
      <BIconCalendarFill />
      <span class="mx-2">Digitized: {{ digitized_date_range[0] }}-{{ digitized_date_range[1] }}</span>
      <BIconXCircle @click="$emit('clear_date_range')" />
    </b-button>
  </b-card>
</template>

<script>
import {
  BIconXCircle,
  BIconFolderFill,
  BIconCalendarFill,
  BIconCamera
} from "bootstrap-vue";

export default {
  name: "FacetPills",
  components: {
    BIconXCircle,
    BIconFolderFill,
    BIconCalendarFill,
    BIconCamera
  },
  props: {
    directory: Object,
    job: Object,
    digitized_date_range: Array
  },
  computed: {
    show_range() {
      return !(
        this.digitized_date_range[0] == 2003 &&
        this.digitized_date_range[1] == 2020
      );
    }
  }
};
</script>
