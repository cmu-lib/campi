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
      <Directory
        v-for="directory in directories"
        :key="directory.id"
        :directory="directory"
        @selected="select_dir($event)"
      />
    </b-list-group>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
// import _ from "lodash";
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
    },
    job: {
      type: Object,
      default: null
    },
    job_tag: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      dir_label_search: "",
      show_all: false
    };
  },
  computed: {
    query_payload() {
      var payload = { ordering: "label" };
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
      if (!!this.job_tag) {
        payload["job_tag"] = this.job_tag.id;
      }
      return payload;
    }
  },
  asyncComputed: {
    directories() {
      return HTTP.get("/directory/", {
        params: this.query_payload
      }).then(
        results => {
          if (this.dir_label_search != "") {
            results.data.forEach(x => {
              x["search_match"] = x.label.includes(this.dir_label_search);
            });
          }
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
      const createDataTree = dataset => {
        let hashTable = Object.create(null);
        dataset.forEach(
          aData => (hashTable[aData.id] = { ...aData, children: [] })
        );
        let dataTree = [];
        dataset.forEach(aData => {
          if (aData.parent_directory) {
            if (aData.parent_directory in hashTable) {
              hashTable[aData.parent_directory].children.push(
                hashTable[aData.id]
              );
            } else {
              dataTree.push(hashTable[aData.id]);
            }
          } else {
            dataTree.push(hashTable[aData.id]);
          }
        });
        return dataTree;
      };

      // Start with the top directory
      return createDataTree(dirlist);
    },
    select_dir(dir) {
      this.$emit("input", dir);
      window.scrollTo(0, 0);
    }
  },
  watch: {
    dir_label_search() {
      if (this.dir_label_search != "") {
        this.show_all = true;
      }
    }
  }
};
</script>