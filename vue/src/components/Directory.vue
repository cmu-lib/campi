<template>
  <b-list-group-item v-if="!!directory" :active="directory.text_match" class="my-0 py-1 mr-0 pr-0">
    <div class="d-flex justify-content-between align-items-center">
      <BIconFolderPlus v-if="(directory.children.length > 0) & !expanded" @click="expanded=true" />
      <BIconFolderMinus
        v-else-if="(directory.children.length > 0) & expanded"
        @click="expanded=false"
      />
      <BIconBlank v-else />
      <span class="ml-2 text-truncate" @click="$emit('selected', directory)">{{ directory.label }}</span>
      <b-badge variant="info" class="ml-auto mr-1">{{ directory.n_images }}</b-badge>
    </div>
    <b-list-group v-if="expanded" class="ml-3 mr-0 pr-0">
      <Directory
        v-for="child in directory.children"
        :key="child.id"
        :directory="child"
        @selected="$emit('selected', $event)"
      />
    </b-list-group>
  </b-list-group-item>
</template>

<script>
import { BIconFolderPlus, BIconFolderMinus, BIconBlank } from "bootstrap-vue";
export default {
  name: "Directory",
  components: {
    BIconFolderPlus,
    BIconFolderMinus,
    BIconBlank
  },
  props: {
    directory: Object
  },
  data() {
    return {
      expanded: false
    };
  }
};
</script>