{{/*
Expand the name of the chart.
*/}}
{{- define "project-ai.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels applied to every resource.
*/}}
{{- define "project-ai.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{/*
Selector labels for a named component.
Usage: include "project-ai.selectorLabels" (dict "root" . "component" "api")
*/}}
{{- define "project-ai.selectorLabels" -}}
app.kubernetes.io/name: {{ include "project-ai.name" .root }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Build full image reference (registry/owner/name:tag)
Usage: include "project-ai.image" (dict "root" . "name" "api")
*/}}
{{- define "project-ai.image" -}}
{{- if .root.Values.image.registry }}
{{- if .root.Values.image.owner }}
{{- printf "%s/%s/project-ai-%s:%s" .root.Values.image.registry .root.Values.image.owner .name (default "latest" .root.Values.image.tag) }}
{{- else }}
{{- printf "%s/project-ai-%s:%s" .root.Values.image.registry .name (default "latest" .root.Values.image.tag) }}
{{- end }}
{{- else }}
{{- printf "project-ai-development-%s" .name }}
{{- end }}
{{- end }}

{{/*
Secret name for a component.
Usage: include "project-ai.secretName" (dict "root" . "component" "api")
*/}}
{{- define "project-ai.secretName" -}}
{{ .root.Release.Name }}-{{ .component }}-secrets
{{- end }}

{{/*
Hardened security context shared by all containers.
*/}}
{{- define "project-ai.securityContext" -}}
readOnlyRootFilesystem: true
allowPrivilegeEscalation: false
capabilities:
  drop: [ALL]
runAsNonRoot: true
seccompProfile:
  type: RuntimeDefault
{{- end }}

{{/*
Hardened pod security context.
*/}}
{{- define "project-ai.podSecurityContext" -}}
runAsNonRoot: true
seccompProfile:
  type: RuntimeDefault
{{- end }}

{{/*
Standard /tmp emptyDir volume used by Python and nginx services.
*/}}
{{- define "project-ai.tmpVolume" -}}
- name: tmp
  emptyDir:
    sizeLimit: 64Mi
{{- end }}

{{- define "project-ai.tmpVolumeMount" -}}
- name: tmp
  mountPath: /tmp
{{- end }}
