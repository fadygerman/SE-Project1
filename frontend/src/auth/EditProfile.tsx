import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useAuth } from '../auth/AuthWrapper';
import { userAttributesType } from './types';

interface EditProfileProps {
  userAttributes: userAttributesType;
  fetchUser: () => Promise<userAttributesType>;
  isVisible: boolean;
}

const EditProfile: React.FC<EditProfileProps> = ({ userAttributes, fetchUser, isVisible }) => {
  const { updateUserAttributes } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    name: '',
    family_name: '',
    phone_number: '',
  });

  useEffect(() => {
    setForm({
      name: userAttributes.name,
      family_name: userAttributes.family_name,
      phone_number: userAttributes.phone_number,
    });
  }, [userAttributes]);

  const handleToggleEdit = async () => {
    if (isEditing) {
      await fetchUser();
    }
    setIsEditing((prev) => !prev);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await updateUserAttributes(form);
      alert('Profile updated!');
      setIsEditing(false);
    } catch (err) {
      console.error(err);
      alert(`${err instanceof Error ? err.message : ''}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'center', margin: '20px' }}>
        <Button onClick={handleToggleEdit}>
          {isEditing ? 'Cancel' : 'Update Profile'}
        </Button>
      </div>

      <div className={`edit-form-wrapper ${isEditing && isVisible ? 'open' : ''}`}>
        <div className="space-y-4 px-4 max-w-md mx-auto pb-4">
          <Input name="name" placeholder="First Name" value={form.name} onChange={handleChange} />
          <Input
            name="family_name"
            placeholder="Last Name"
            value={form.family_name}
            onChange={handleChange}
          />
          <Input
            name="phone_number"
            placeholder="Phone Number"
            value={form.phone_number}
            onChange={handleChange}
          />
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <Button onClick={handleConfirm} disabled={loading}>
              {loading ? 'Saving...' : 'Confirm'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditProfile;
