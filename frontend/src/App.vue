<template>
  <div class="container py-4">
    <header class="pb-3 mb-4 border-bottom">
      <h1 class="fw-bold">{{ $t("app.title") }}</h1>
      <p class="text-muted">{{ $t("app.description") }}</p>
    </header>

    <!-- App Info Section -->
    <div class="row mb-4 bg-light rounded p-4">
      <div class="col-md-7">
        <h4 class="mb-3">{{ $t("app.aboutApp.title") }}</h4>
        <p v-html="$t('app.aboutApp.description')"></p>
        <div class="card mb-3 bg-white">
          <div class="card-body">
            <h5 class="card-title">{{ $t("app.aboutApp.caution") }}</h5>
            <p class="card-text">{{ $t("app.aboutApp.cautionText") }}</p>
          </div>
        </div>
        <div class="d-flex gap-3 mt-3">
          <a
            href="https://github.com/soh7410/image-title_generator"
            target="_blank"
            class="btn btn-outline-primary"
          >
            <i class="bi bi-github me-2"></i>GitHub
          </a>
          <a
            href="https://x.com/soh_______"
            target="_blank"
            class="btn btn-outline-dark"
          >
            <i class="bi bi-twitter-x me-2"></i>{{ $t("app.aboutApp.creator") }}
          </a>
        </div>
      </div>
      <div class="col-md-5">
        <div class="diagram-container p-3 bg-white rounded shadow-sm">
          <h5 class="text-center mb-3">{{ $t("app.flowDiagram.title") }}</h5>
          <div class="process-diagram">
            <div class="process-step">
              <div class="step-icon upload-icon">
                <i class="bi bi-cloud-upload"></i>
              </div>
              <div class="step-text">
                {{ $t("app.flowDiagram.uploadStep") }}
              </div>
            </div>
            <div class="process-arrow">→</div>
            <div class="process-step">
              <div class="step-icon api-icon">
                <i class="bi bi-cpu"></i>
              </div>
              <div class="step-text">{{ $t("app.flowDiagram.apiStep") }}</div>
            </div>
            <div class="process-arrow">→</div>
            <div class="process-step">
              <div class="step-icon title-icon">
                <i class="bi bi-tag"></i>
              </div>
              <div class="step-text">{{ $t("app.flowDiagram.titleStep") }}</div>
            </div>
            <div class="process-arrow">→</div>
            <div class="process-step">
              <div class="step-icon download-icon">
                <i class="bi bi-file-zip"></i>
              </div>
              <div class="step-text">
                {{ $t("app.flowDiagram.downloadStep") }}
              </div>
            </div>
          </div>
          <div class="text-center mt-3">
            <small class="text-muted">{{
              $t("app.aboutApp.privacyNote")
            }}</small>
          </div>
        </div>
      </div>
    </div>

    <main>
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card">
            <div class="card-body">
              <!-- Language selection -->
              <div class="mb-3">
                <label class="form-label">{{ $t("app.language") }}</label>
                <select
                  v-model="selectedLanguage"
                  class="form-select"
                  style="max-width: 200px"
                >
                  <option value="en">{{ $t("app.languageOptions.en") }}</option>
                  <option value="ja">{{ $t("app.languageOptions.ja") }}</option>
                </select>
              </div>

              <!-- File upload -->
              <div
                class="upload-area p-4 mb-3 text-center border rounded"
                :class="{
                  'border-primary': isDragging,
                  disabled: isProcessing,
                }"
                @dragover.prevent="!isProcessing && (isDragging = true)"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="!isProcessing && onFileDrop"
                @click="!isProcessing && $refs.fileInput.click()"
              >
                <div v-if="!files.length">
                  <div class="mb-3">
                    <i class="bi bi-cloud-upload fs-1"></i>
                  </div>
                  <p>{{ $t("app.dropzone") }}</p>
                </div>
                <div v-else class="text-start">
                  <h5>
                    {{ files.length }}
                    {{
                      files.length > 1 ? $t("app.files") : $t("app.file")
                    }}
                    selected:
                  </h5>
                  <ul class="list-group">
                    <li
                      v-for="(file, index) in files"
                      :key="index"
                      class="list-group-item d-flex justify-content-between align-items-center"
                    >
                      <span>{{ file.name }}</span>
                      <div class="d-flex align-items-center">
                        <span
                          v-if="fileStatus[index]"
                          class="me-2 badge"
                          :class="getStatusBadgeClass(fileStatus[index])"
                        >
                          {{ getStatusText(fileStatus[index]) }}
                        </span>
                        <button
                          type="button"
                          class="btn btn-sm btn-outline-danger"
                          @click.stop="removeFile(index)"
                          :disabled="isProcessing"
                        >
                          ×
                        </button>
                      </div>
                    </li>
                  </ul>
                </div>
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept="image/*"
                  style="display: none"
                  @change="onFileChange"
                  :disabled="isProcessing"
                />
              </div>

              <!-- Processing status display -->
              <div v-if="isProcessing" class="processing-status mb-3">
                <div class="progress mb-2">
                  <div
                    class="progress-bar progress-bar-striped progress-bar-animated"
                    role="progressbar"
                    :style="{ width: `${calculateProgress()}%` }"
                  ></div>
                </div>

                <div
                  class="status-info d-flex justify-content-between align-items-center"
                >
                  <div class="status-text">
                    <strong>{{ $t("app.processingStatus") }}:</strong>
                    {{ getCurrentStepText() }}
                  </div>
                  <div class="status-counter">
                    <span class="badge bg-info"
                      >{{ processedCount }}/{{ files.length }}</span
                    >
                  </div>
                </div>

                <div class="estimated-time text-muted mt-1">
                  <small>{{ getEstimatedTimeText() }}</small>
                </div>
              </div>

              <!-- Process button -->
              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button
                  class="btn btn-primary"
                  @click="processImages"
                  :disabled="isProcessing || !files.length"
                >
                  <span
                    v-if="isProcessing"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  {{ $t("app.processButton") }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Results display area -->
      <div
        v-if="message"
        class="alert"
        :class="messageType === 'success' ? 'alert-success' : 'alert-danger'"
      >
        {{ message }}
      </div>
    </main>

    <footer class="pt-3 mt-4 text-muted border-top">
      &copy; {{ new Date().getFullYear() }} Image Title Generator
    </footer>
  </div>
</template>

<script>
import axios from "axios";
import { useI18n } from "vue-i18n";
import { ref, watch, reactive, computed } from "vue";

export default {
  name: "App",
  setup() {
    const { t, locale } = useI18n();

    const files = ref([]);
    const isDragging = ref(false);
    const isProcessing = ref(false);
    const message = ref("");
    const messageType = ref("");
    const selectedLanguage = ref("en");
    const fileInput = ref(null);

    // Variables for tracking processing status
    const currentStep = ref(0);
    const processedCount = ref(0);
    const startTime = ref(null);
    const fileStatus = reactive({});
    const processingSteps = [
      "uploading", // Uploading images
      "caption", // Generating captions
      "title", // Creating titles
      "packaging", // Creating ZIP file
      "complete", // Complete
    ];

    // Handle language change
    watch(selectedLanguage, (newLang) => {
      locale.value = newLang;
    });

    // Handle file drop
    const onFileDrop = (event) => {
      isDragging.value = false;
      const droppedFiles = event.dataTransfer.files;
      addFiles(droppedFiles);
    };

    // Handle file selection
    const onFileChange = (event) => {
      addFiles(event.target.files);
    };

    // Add files to the list
    const addFiles = (fileList) => {
      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        if (file.type.startsWith("image/")) {
          const fileIndex = files.value.length;
          files.value.push(file);
          fileStatus[fileIndex] = "pending";
        }
      }
    };

    // Remove a file
    const removeFile = (index) => {
      files.value.splice(index, 1);
      // Update file status indexes
      const newFileStatus = {};
      Object.keys(fileStatus).forEach((key) => {
        const keyNum = parseInt(key);
        if (keyNum < index) {
          newFileStatus[keyNum] = fileStatus[keyNum];
        } else if (keyNum > index) {
          newFileStatus[keyNum - 1] = fileStatus[keyNum];
        }
      });
      Object.keys(fileStatus).forEach((key) => {
        delete fileStatus[key];
      });
      Object.keys(newFileStatus).forEach((key) => {
        fileStatus[key] = newFileStatus[key];
      });
    };

    // Calculate processing progress
    const calculateProgress = () => {
      if (files.value.length === 0) return 0;
      if (currentStep.value === 0) return 5; // Starting
      if (currentStep.value === processingSteps.length - 1) return 100; // Completed

      // Calculate progress based on steps and processed files
      const stepsWeight = 0.2; // Step weight factor
      const filesWeight = 0.8; // File processing weight factor

      const stepsProgress =
        (currentStep.value / (processingSteps.length - 1)) * 100 * stepsWeight;
      const filesProgress =
        (processedCount.value / files.value.length) * 100 * filesWeight;

      return Math.min(95, stepsProgress + filesProgress); // Max 95% before download
    };

    // Get text for current processing step
    const getCurrentStepText = () => {
      const step = processingSteps[currentStep.value];
      return t(`app.processingSteps.${step}`);
    };

    // Get estimated time remaining text
    const getEstimatedTimeText = () => {
      if (!startTime.value || processedCount.value === 0) {
        return t("app.estimatingTime");
      }

      const elapsedTime = (Date.now() - startTime.value) / 1000; // In seconds
      const timePerFile = elapsedTime / processedCount.value;
      const remainingFiles = files.value.length - processedCount.value;
      const estimatedSeconds = timePerFile * remainingFiles;

      if (estimatedSeconds < 60) {
        return t("app.estimatedTimeSeconds", {
          seconds: Math.ceil(estimatedSeconds),
        });
      } else {
        const minutes = Math.floor(estimatedSeconds / 60);
        const seconds = Math.ceil(estimatedSeconds % 60);
        return t("app.estimatedTimeMinutes", { minutes, seconds });
      }
    };

    // Get badge class based on file status
    const getStatusBadgeClass = (status) => {
      switch (status) {
        case "processing":
          return "bg-primary";
        case "caption":
          return "bg-info";
        case "title":
          return "bg-info";
        case "complete":
          return "bg-success";
        case "error":
          return "bg-danger";
        default:
          return "bg-secondary";
      }
    };

    // Get status text
    const getStatusText = (status) => {
      return t(`app.fileStatus.${status}`);
    };

    // Process images request
    const processImages = async () => {
      if (!files.value.length) {
        message.value = t("app.noFiles");
        messageType.value = "error";
        return;
      }

      try {
        isProcessing.value = true;
        message.value = "";
        currentStep.value = 0;
        processedCount.value = 0;
        startTime.value = Date.now();

        // Update status for all files
        files.value.forEach((_, index) => {
          fileStatus[index] = "pending";
        });

        // Start upload step
        currentStep.value = 0;
        await new Promise((resolve) => setTimeout(resolve, 500)); // Short delay to update UI

        const formData = new FormData();
        files.value.forEach((file, index) => {
          formData.append("files", file);
          fileStatus[index] = "processing";
        });
        formData.append("language", selectedLanguage.value);

        // Start caption generation step
        currentStep.value = 1;
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Short delay to update UI

        // Simulate file processing stages
        // This would ideally be replaced with real status updates from the server
        const simulateFileProcessing = async () => {
          for (let i = 0; i < files.value.length; i++) {
            fileStatus[i] = "caption";
            await new Promise((resolve) =>
              setTimeout(resolve, 500 + Math.random() * 1000)
            );

            fileStatus[i] = "title";
            await new Promise((resolve) =>
              setTimeout(resolve, 500 + Math.random() * 500)
            );

            fileStatus[i] = "complete";
            processedCount.value++;
            await new Promise((resolve) => setTimeout(resolve, 200));
          }
        };

        // Start progress simulation
        // Run in parallel with the actual API call
        const simulationPromise = simulateFileProcessing();

        const response = await axios.post("/api/process-images", formData, {
          responseType: "blob",
        });

        // Start ZIP creation step
        currentStep.value = 3;

        // Create download link
        const blob = new Blob([response.data], { type: "application/zip" });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "renamed_images.zip");
        document.body.appendChild(link);
        link.click();
        link.remove();

        // Complete step
        currentStep.value = 4;

        // Wait for simulation completion
        await simulationPromise;

        // Show success message
        message.value = t("app.success");
        messageType.value = "success";

        // Clear file list
        files.value = [];
        if (fileInput.value) {
          fileInput.value.value = "";
        }

        // Reset status
        Object.keys(fileStatus).forEach((key) => {
          delete fileStatus[key];
        });
      } catch (error) {
        console.error("Error processing images:", error);
        message.value = `${t("app.error")}: ${
          error.message || "Unknown error"
        }`;
        messageType.value = "error";

        // Mark error status
        files.value.forEach((_, index) => {
          if (fileStatus[index] !== "complete") {
            fileStatus[index] = "error";
          }
        });
      } finally {
        isProcessing.value = false;
      }
    };

    return {
      files,
      isDragging,
      isProcessing,
      message,
      messageType,
      selectedLanguage,
      fileInput,
      fileStatus,
      currentStep,
      processedCount,
      onFileDrop,
      onFileChange,
      removeFile,
      processImages,
      calculateProgress,
      getCurrentStepText,
      getEstimatedTimeText,
      getStatusBadgeClass,
      getStatusText,
    };
  },
};
</script>

<style scoped>
.upload-area {
  min-height: 200px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

.upload-area:hover:not(.disabled) {
  background-color: #e9ecef;
}

.upload-area.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.processing-status {
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 1rem;
  background-color: #f8f9fa;
}

.status-info {
  margin-top: 0.5rem;
}

.estimated-time {
  font-size: 0.875rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

/* App Info Section Styles */
.process-diagram {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 85px;
}

.step-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-bottom: 8px;
  font-size: 1.5rem;
  color: white;
}

.upload-icon {
  background-color: #6c757d;
}

.api-icon {
  background-color: #0d6efd;
}

.title-icon {
  background-color: #198754;
}

.download-icon {
  background-color: #dc3545;
}

.step-text {
  font-size: 0.75rem;
  text-align: center;
}

.process-arrow {
  font-size: 1.2rem;
  color: #6c757d;
  margin: 0 5px;
  display: flex;
  align-items: center;
  padding-bottom: 15px;
}

@media (max-width: 767px) {
  .process-diagram {
    flex-direction: column;
  }

  .process-arrow {
    transform: rotate(90deg);
    margin: 10px 0;
    padding: 0;
  }
}
</style>