import {checkGallery} from "./gallery_reader_checks.mjs";
await checkGallery("analysis-gallery",process.argv[2]+"-completion");
await checkGallery("analysis-library",process.argv[2]);
