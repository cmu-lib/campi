<template>
  <b-media>
    <template v-slot:aside>
      <b-img :src="photograph.image.thumbnail" width="200" />
    </template>
    <b-link :to="{name: 'Similarity', params: {id: photograph.id}, scrollBehavior: { x: 0, y: 0 }}">
      <h6>{{ photograph.filename }}</h6>
    </b-link>
    <b-progress
      v-if="photograph.distance"
      :value="1-photograph.distance"
      max="1"
      variant="secondary"
      v-b-popover.hover.top="'Similarity is measured based on the cosine distance of this photograph\'s vector from the vector of the seed image.'"
      :title="'Distance: ' + photograph.distance"
    />
    <p>{{ photograph.date_taken_early }} - {{ photograph.date_taken_late }}</p>
    <b-row>
      <b-badge
        v-if="!!photograph.job"
        class="mx-2"
        :to="{name: 'Browse', query: {job: photograph.job.id}}"
      >
        <BIconCamera />
        {{ photograph.job.label }}
      </b-badge>
      <b-badge class="mx-2" :to="{name: 'Browse', query: {job: photograph.directory.id}}">
        <BIconFolderFill />
        {{ photograph.directory.label }}
      </b-badge>
    </b-row>
  </b-media>
</template>

<script>
import { BIconCamera, BIconFolderFill } from "bootstrap-vue";
export default {
  name: "PhotographListItem",
  components: { BIconCamera, BIconFolderFill },
  props: {
    photograph: {
      type: Object,
      required: true
    }
  },
  methods: {
    get_variant(distance) {
      if (distance <= 0.39) {
        return "success";
      } else if ((distance > 0.39) & (distance <= 0.55)) {
        return "warning";
      } else {
        return "secondary";
      }
    }
  }
};
</script>