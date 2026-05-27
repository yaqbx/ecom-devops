{{- define "database.name" -}}
{{ .Values.nameOverride | default .Chart.Name }}
{{- end -}}

{{- define "database.fullname" -}}
{{ .Values.fullnameOverride | default .Release.Name }}
{{- end -}}

{{- define "database.labels" -}}
app: {{ include "database.name" . }}
release: {{ .Release.Name }}
{{- end -}}
