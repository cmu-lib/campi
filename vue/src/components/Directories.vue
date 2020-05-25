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
        class="p-1"
        v-for="dir in directories.results"
        :key="dir.id"
        :id="dir.id"
        @click="select_dir(dir)"
      />
    </b-list-group>
  </b-card>
</template>

<script>
import { HTTP } from "../main";
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
      var payload = { is_top: true };
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
          return results.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  methods: {
    select_dir(dir) {
      this.$emit("input", dir);
      window.scrollTo(0, 0);
    }
  }
};
</script>