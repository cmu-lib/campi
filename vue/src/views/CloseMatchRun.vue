<template>
  <b-container fluid>
    <b-row align-v="center">
      <b-col cols="11">
        <CloseMatchRunBar v-if="!!close_match_run" :close_match_run="close_match_run" />
      </b-col>
      <b-col cols="1">
        <b-button v-b-toggle.cmr-help variant="primary">
          <BIconQuestionCircleFill class="mx-1" />
          <span>Toggle Instructions</span>
        </b-button>
      </b-col>
    </b-row>

    <b-collapse id="cmr-help" class="my-2">
      <b-card header="Instructions">
        <b-card-text class="instructions">
          <h3>What is a "match set"?</h3>
          <p>We generated each "match set" by having the computer look for densely-packed clusters of images that were all very close to each other in the image-similarity-space. We ran this clustering twice: first with a fine-grained search that only put together very similar images, and then again with a slightly coarser-grained search that found bigger clusters of images.</p>
          <p>
            Those photographs that are
            <span class="core-color">colored blue are the "core" imgages</span> found in this first round. These images will only show up in this match set. Once matched as "core" in this set, they won't be considered for future sets.
            <strong>Base your set decisions on these photos first.</strong> As you process more sets, you may get to a set where you have already accepted its core photos, so no
            <span class="core-color">blue photos</span> will be present. In this case, feel free to pick out a set from the remaining photos.
          </p>
          <p>Every other image is a secondary image added on as an additional option to add to the set from that coarser-grained clustering. This handles cases where photos may not be close enough in visual distance to fall under the "core" threshold, but which editors might want to include in the set.</p>
          <h3>Accept / Reject / Exclude</h3>
          <p>You have three options for marking photographs:</p>
          <ol>
            <li>
              Accept
              <BIconCheck2 />: Yes, this photograph belongs to this set. Once you save this choice, that photograph will be removed from all other future match sets - you can't double-assign photographs to sets.
            </li>
            <li>
              Reject
              <BIconX />: No, this photograph doesn't belong in this set. If that photograph is a non-core photo, one that has been proposed for multiple sets, then you may see it again in a later set and have the chance to mark it as part of that later set.
            </li>
            <li>
              Exclude
              <BIconExclamationOctagonFill />: No, this photo doesn't belong in this set,
              <strong>and I want to premptorily exclude it from all other sets. It should NEVER be matched up.</strong> This is usfeul for photos you are sure will never get usefully matched (like document versos or large pictures of crowds) and will help make a lot of sets redundant.
            </li>
          </ol>
          <p>
            Once you make your selections, and choose a "primary" photo by clicking the
            <BIconStar />button, click "Save" to commit those choices to the database.
          </p>
          <h3>Other tools</h3>
          <p>
            Mouse over the
            <BIconFolderFill />button to see the name of the directory that this photo belongs to. Click it to open up a sidebar where you can browse all the other photos in that directory. You can do the same for the job with the
            <BIconCamera />button.
          </p>
          <p>Click on a photo in this sidebar to force-add it to this match set. Always remember to click "Save" to commit your decisions to the database.</p>
          <p>
            The
            <BIconSearch />button appears on non-core photos, and will let you pull up the other match sets where this photograph may appear. (Note: it's possible that non-core photographs don't appear in other sets)
          </p>
          <p>Use the "Photo order" menu to quickly re-sort the photos based on similarity vs. filename, etc. This doesn't affect any of the final data, it's just a discovery tool that can make it easier to sort through some of the larger sets to figure out which pictures should be included or not.</p>
        </b-card-text>
      </b-card>
    </b-collapse>
    <router-view @set_submitted="set_submitted" />
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchRunBar from "@/components/close_match/CloseMatchRunBar.vue";
import {
  BIconQuestionCircleFill,
  BIconStar,
  BIconCheck2,
  BIconX,
  BIconCamera,
  BIconFolderFill,
  BIconSearch,
  BIconExclamationOctagonFill
} from "bootstrap-vue";
export default {
  name: "CloseMatchRun",
  components: {
    CloseMatchRunBar,
    BIconQuestionCircleFill,
    BIconStar,
    BIconCheck2,
    BIconX,
    BIconCamera,
    BIconFolderFill,
    BIconSearch,
    BIconExclamationOctagonFill
  },
  props: {
    close_match_run_id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      close_match_run: null
    };
  },
  methods: {
    get_close_match_run() {
      if (!!this.close_match_run_id) {
        return HTTP.get(`/close_match/run/${this.close_match_run_id}/`, {
          params: this.query_payload
        }).then(
          results => {
            this.close_match_run = results.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    },
    set_submitted() {
      this.get_close_match_run();
    }
  },
  mounted() {
    this.get_close_match_run(this.$route.params.id);
  }
};
</script>

<style lang="scss">
span.core-color {
  background-color: #b2ddfa;
}

.instructions > p,
li {
  font-size: large;
}
</style>