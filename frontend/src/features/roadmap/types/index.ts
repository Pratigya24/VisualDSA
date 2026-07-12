export interface RoadmapTopic {
  id: string;
  name: string;
  slug: string;
  description: string;
  order: number;
  prerequisiteIds: string[];
  icon: string | null;
  isUnlocked: boolean;
  algorithmCount: number;
  solvedCount: number;
}
