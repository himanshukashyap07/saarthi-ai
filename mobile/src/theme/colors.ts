export const colors = {
  teal: "#04694F",
  tealDark: "#0B3D33",
  orange: "#EB5500",
  orangeLight: "#F7A56C",
  dark: "#212529",
  gray: "#5A5A5A",
  lightGray: "#E4E6E8",
  bg: "#F5F8F7",
  white: "#FFFFFF",
  danger: "#C0392B",
  warning: "#D98324",
  success: "#1E8E5A",
};

export const severityColor = (severity: string) => {
  switch (severity) {
    case "high":
      return colors.danger;
    case "medium":
      return colors.warning;
    default:
      return colors.success;
  }
};

export const engagementColor = (level: string) => {
  switch (level) {
    case "High":
      return colors.success;
    case "Medium":
      return colors.warning;
    case "Low":
      return colors.danger;
    default:
      return colors.gray;
  }
};

export const scoreColor = (score: number) => {
  if (score >= 75) return colors.success;
  if (score >= 50) return colors.warning;
  return colors.gray;
};
