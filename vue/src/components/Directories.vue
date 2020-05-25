<template>
  <b-card class="my-2" header="Directories">
    <b-input-group class="my-2">
      <b-input v-model="dir_label_search" debounce="500" placeholder="Search directory names..." />
      <b-input-group-append v-if="dir_label_search != ''">
        <b-button variant="warning" size="sm" @click="dir_label_search=''">
          <BIconXSquare />
        </b-button>
      </b-input-group-append>
    </b-input-group>
    <b-list-group v-if="!!directories">
      <Directory :directory="directories" @click="select_dir($event)" />
    </b-list-group>
  </b-card>
</template>

<script>
import { HTTP } from "../main";
import _ from "lodash";
import { BIconXSquare } from "bootstrap-vue";
import Directory from "@/components/Directory.vue";
export default {
  name: "Directories",
  components: {
    BIconXSquare,
    Directory
  },
  props: {
    digitized_date_before: {
      type: Number,
      default: null
    },
    digitized_date_after: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      dir_label_search: "",
      show_all: false
    };
  },
  asyncComputed: {
    directories() {
      var payload = {};
      if (this.dir_label_search != "") {
        payload["label"] = this.dir_label_search;
      }
      if (!!this.digitized_date_after) {
        payload["digitized_date_after"] = `${this.digitized_date_after}-01-01`;
      }
      if (!!this.digitized_date_before) {
        payload[
          "digitized_date_before"
        ] = `${this.digitized_date_before}-01-01`;
      }
      return HTTP.get("/directory/", {
        params: payload
      }).then(
        results => {
          return this.nest_directories(results.data);
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  methods: {
    nest_directories(dirlist) {
      const find_parent = function(tree, dir) {
        console.log("Checking " + dir.label);
        if (tree.id == dir.parent_directory) {
          console.log(dir.label + " child of " + tree.label);
          // Prepare the directory to gain children
          dir["children"] = [];
          tree.children.push(dir);
          return tree;
        } else {
          for (var i = 0; i < tree.children.length; i++) {
            console.log(
              "Going down the stack to child " + tree.children[i].label
            );
            const res = find_parent(tree.children[i], dir);
            if (_.isObject(res)) {
              tree.children[i].children.push(res);
            } else {
              return tree;
            }
          }
        }
      };

      // Start with the top directory
      var dirtree = dirlist[0];
      dirtree["children"] = [];
      console.log("Root is " + dirtree.label);
      console.log(dirlist.length + " total directories");
      for (var a = 1; a < dirlist.length; a++) {
        console.log("Looping at: " + a);
        dirtree = find_parent(dirtree, dirlist[a]);
      }
      console.log(dirtree);
      return dirtree;
    },
    select_dir(dir) {
      this.$emit("input", dir);
      window.scrollTo(0, 0);
    }
  },
  mounted() {
    console.log(this.directories);
  }
};
</script>