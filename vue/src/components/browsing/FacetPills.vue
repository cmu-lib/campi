<template>
  <b-card class="my-2">
    <b-button class="mx-1" v-if="freetext!=''" pill variant="light" size="sm">
      <BIconTag />
      <span class="mx-2">{{ freetext }}</span>
      <BIconXCircle @click="$emit('clear_freetext')" />
    </b-button>
    <b-button class="mx-1" v-if="!!tag" pill variant="warning" size="sm">
      <BIconTag />
      <span class="mx-2">{{ tag.label }}</span>
      <BIconXCircle @click="$emit('clear_tag')" />
    </b-button>
    <b-button class="mx-1" v-if="!!gcv_object" pill variant="danger" size="sm">
      <BIconColumnsGap />
      <span class="mx-2">{{ gcv_object.label }}</span>
      <BIconXCircle @click="$emit('clear_gcv_object')" />
    </b-button>
    <b-button class="mx-1" v-if="!!gcv_label" pill variant="danger" size="sm">
      <BIconCardList />
      <span class="mx-2">{{ gcv_label.label }}</span>
      <BIconXCircle @click="$emit('clear_gcv_label')" />
    </b-button>
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
  BIconCamera,
  BIconTag,
  BIconColumnsGap,
  BIconCardList,
} from "bootstrap-vue";

export default {
  name: "FacetPills",
  components: {
    BIconXCircle,
    BIconFolderFill,
    BIconCalendarFill,
    BIconCamera,
    BIconTag,
    BIconColumnsGap,
    BIconCardList,
  },
  props: {
    freetext: String,
    directory: Object,
    job: Object,
    tag: Object,
    gcv_object: Object,
    gcv_label: Object,
    digitized_date_range: Array,
  },
  computed: {
    show_range() {
      return !(
        this.digitized_date_range[0] == 2016 &&
        this.digitized_date_range[1] == 2020
      );
    },
  },
};
</script>
