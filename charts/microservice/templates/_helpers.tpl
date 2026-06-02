{{- define "microservice.name" -}}
{{ .Values.nameOverride | default .Chart.Name }}
{{- end -}}

{{- define "microservice.fullname" -}}
{{ .Values.fullnameOverride | default .Release.Name }}
{{- end -}}

{{- define "microservice.labels" -}}
app: {{ include "microservice.name" . }}
release: {{ .Release.Name }}
{{- end -}}
