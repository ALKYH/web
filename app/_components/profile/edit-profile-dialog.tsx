'use client';

import { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import { Edit, Loader2, Camera, Upload } from 'lucide-react';
import { User } from '@/lib/api';
import { uploadUserAvatar, type ProfileUpdateData } from '@/lib/api';

interface EditProfileDialogProps {
  user: User;
  onSave: (updatedData: ProfileUpdateData) => Promise<void>;
  trigger?: React.ReactNode;
}

export function EditProfileDialog({
  user,
  onSave,
  trigger
}: EditProfileDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState<ProfileUpdateData>({
    bio: '',
    location: '',
    website: '',
    birth_date: '',
    title: '',
    expertise: [],
    experience_years: 0,
    hourly_rate: 0,
    urgency_level: 1,
    budget_min: 0,
    budget_max: 0,
    learning_goals: ''
  });

  // Load user data when dialog opens
  useEffect(() => {
    if (open && user) {
      setDataLoading(true);
      // Fetch fresh profile data when dialog opens
      import('@/lib/api').then(({ getUserProfile }) => {
        getUserProfile()
          .then(profile => {
            setFormData({
              bio: profile.bio || '',
              location: profile.location || '',
              website: profile.website || '',
              birth_date: profile.birthDate || '',
              title: profile.title || '',
              expertise: profile.expertise || [],
              experience_years: profile.experienceYears || 0,
              hourly_rate: profile.hourlyRate ? parseFloat(profile.hourlyRate) : 0,
              urgency_level: profile.urgencyLevel || 1,
              budget_min: profile.budgetMin ? parseFloat(profile.budgetMin) : 0,
              budget_max: profile.budgetMax ? parseFloat(profile.budgetMax) : 0,
              learning_goals: profile.learningGoals || ''
            });
          })
          .catch(err => {
            console.error('Failed to load profile data:', err);
            // Fallback to default values
            setFormData({
              bio: user.bio || '',
              location: '',
              website: '',
              birth_date: '',
              title: '',
              expertise: [],
              experience_years: 0,
              hourly_rate: 0,
              urgency_level: 1,
              budget_min: 0,
              budget_max: 0,
              learning_goals: ''
            });
          })
          .finally(() => {
            setDataLoading(false);
          });
      });
    }
  }, [open, user]);

  const handleInputChange = (field: string, value: string | number | string[]) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAvatarUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('请上传 JPG, PNG, GIF 或 WEBP 格式的图片');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('图片文件大小不能超过 5MB');
      return;
    }

    setAvatarUploading(true);
    try {
      const result = await uploadUserAvatar(file);
      setFormData(prev => ({
        ...prev,
        avatarUrl: result.avatar_url
      }));
    } catch (error) {
      console.error('Avatar upload failed:', error);
      alert('头像上传失败，请重试');
    } finally {
      setAvatarUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await onSave(formData);
      setOpen(false);
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Edit className="mr-2 h-4 w-4" />
            编辑个人资料
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>编辑个人资料</DialogTitle>
          <DialogDescription>更新您的个人信息和偏好设置</DialogDescription>
        </DialogHeader>
        <div className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="bio">个人简介</Label>
            {dataLoading ? (
              <Skeleton className="h-20 w-full" />
            ) : (
              <Textarea
                id="bio"
                value={formData.bio || ''}
                onChange={e => handleInputChange('bio', e.target.value)}
                placeholder="介绍一下自己..."
                rows={3}
              />
            )}
          </div>

          <div className="space-y-2">
            <Label>头像</Label>
            {dataLoading ? (
              <Skeleton className="h-32 w-full" />
            ) : (
              <div className="space-y-4">
                {/* Current Avatar Preview */}
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-full overflow-hidden bg-gray-100 border-2 border-gray-200">
                      {/* Avatar preview temporarily disabled - avatarUrl not in ProfileUpdateData */}
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <Camera className="w-8 h-8" />
                      </div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleUploadClick}
                      disabled={avatarUploading}
                      className="w-full"
                    >
                      {avatarUploading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          上传中...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          上传新头像
                        </>
                      )}
                    </Button>
                    <p className="text-xs text-gray-500 mt-1">
                      支持 JPG, PNG, GIF, WEBP 格式，文件大小不超过 5MB
                    </p>
                  </div>
                </div>

                {/* Hidden File Input */}
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleAvatarUpload}
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  className="hidden"
                />

              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="location">所在地</Label>
              {dataLoading ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <Input
                  id="location"
                  value={formData.location || ''}
                  onChange={e => handleInputChange('location', e.target.value)}
                  placeholder="您的所在地"
                />
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="website">个人网站</Label>
              {dataLoading ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <Input
                  id="website"
                  type="url"
                  value={formData.website || ''}
                  onChange={e => handleInputChange('website', e.target.value)}
                  placeholder="https://example.com"
                />
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="birth_date">出生日期</Label>
              {dataLoading ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <Input
                  id="birth_date"
                  type="date"
                  value={formData.birth_date || ''}
                  onChange={e => handleInputChange('birth_date', e.target.value)}
                />
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="title">导师职称</Label>
              {dataLoading ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <Input
                  id="title"
                  value={formData.title || ''}
                  onChange={e => handleInputChange('title', e.target.value)}
                  placeholder="您的职称/职位"
                />
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="experience_years">经验年限</Label>
            {dataLoading ? (
              <Skeleton className="h-10 w-full" />
            ) : (
              <Input
                id="experience_years"
                type="number"
                min="0"
                value={formData.experience_years || 0}
                onChange={e => handleInputChange('experience_years', parseInt(e.target.value) || 0)}
                placeholder="0"
              />
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="hourly_rate">时薪 (CNY)</Label>
            {dataLoading ? (
              <Skeleton className="h-10 w-full" />
            ) : (
              <Input
                id="hourly_rate"
                type="number"
                min="0"
                step="0.01"
                value={formData.hourly_rate || 0}
                onChange={e => handleInputChange('hourly_rate', parseFloat(e.target.value) || 0)}
                placeholder="0.00"
              />
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="budget_min">最小预算</Label>
              {dataLoading ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <Input
                  id="budget_min"
                  type="number"
                  min="0"
                  value={formData.budget_min || 0}
                  onChange={e => handleInputChange('budget_min', parseFloat(e.target.value) || 0)}
                  placeholder="0"
                />
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget_max">最大预算</Label>
              {dataLoading ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <Input
                  id="budget_max"
                  type="number"
                  min="0"
                  value={formData.budget_max || 0}
                  onChange={e => handleInputChange('budget_max', parseFloat(e.target.value) || 0)}
                  placeholder="0"
                />
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="learning_goals">学习目标</Label>
            {dataLoading ? (
              <Skeleton className="h-20 w-full" />
            ) : (
              <Textarea
                id="learning_goals"
                value={formData.learning_goals || ''}
                onChange={e => handleInputChange('learning_goals', e.target.value)}
                placeholder="描述您的学习目标..."
                rows={3}
              />
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSave} disabled={loading || dataLoading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  保存中...
                </>
              ) : (
                '保存'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
