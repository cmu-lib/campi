<template>
  <b-list-group-item v-if="!!directory" class="p-1" :active="directory.text_match">
    <BIconFolderPlus v-if="(directory.children.length > 0) & !expanded" @click="expanded=true" />
    <BIconFolderMinus
      v-else-if="(directory.children.length > 0) & expanded"
      @click="expanded=false"
    />
    <BIconBlank v-else />
    <span
      class="ml-2"
      @click="$emit('selected', directory)"
    >{{ directory.label }} ({{ directory.n_images }})</span>
    <b-list-group v-if="expanded" class="ml-3">
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