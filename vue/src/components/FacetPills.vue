<template>
  <b-card>
    <b-button v-if="!!directory" pill variant="primary" size="sm">
      <BIconFolderFill />
      <span class="mx-2">{{ directory.label }}</span>
      <BIconXCircle @click="$emit('clear_directory')" />
    </b-button>
  </b-card>
</template>

<script>
import { BIconXCircle, BIconFolderFill } from "bootstrap-vue";

export default {
  name: "FacetPills",
  components: {
    BIconXCircle,
    BIconFolderFill
  },
  props: {
    directory: Object
  }
};
</script>