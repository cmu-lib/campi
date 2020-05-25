<template>
  <b-list-group-item v-if="!!directory" class="p-1">
    <BIconFolderPlus
      v-if="(directory.child_directories.length > 0) & !expanded"
      @click="expanded=true"
    />
    <BIconFolderMinus
      v-else-if="(directory.child_directories.length > 0) & expanded"
      @click="expanded=false"
    />
    <BIconBlank v-else />
    <span>{{ directory.label }} ({{ directory.n_images }})</span>
    <b-list-group v-if="expanded" class="ml-3">
      <Directory v-for="child in directory.child_directories" :key="child.id" :id="child.id" />
    </b-list-group>
  </b-list-group-item>
</template>

<script>
import { HTTP } from "../main";
import { BIconFolderPlus, BIconFolderMinus, BIconBlank } from "bootstrap-vue";
export default {
  name: "Directory",
  components: {
    BIconFolderPlus,
    BIconFolderMinus,
    BIconBlank
  },
  props: {
    id: Number
  },
  data() {
    return {
      expanded: false
    };
  },
  asyncComputed: {
    directory() {
      return HTTP.get("/directory/" + this.id + "/").then(
        results => {
          return results.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>