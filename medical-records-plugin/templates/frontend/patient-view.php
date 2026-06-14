<div class="mr-patient-container">
    <h2><?php _e('پرونده پزشکی من', 'medical-records'); ?></h2>
    
    <?php
    $current_user = wp_get_current_user();
    global $wpdb;
    $bookly_customer = $wpdb->get_row($wpdb->prepare(
        "SELECT id, full_name, phone, email FROM {$wpdb->prefix}bookly_customers WHERE wp_user_id = %d",
        $current_user->ID
    ), ARRAY_A);
    
    if (!$bookly_customer) :
    ?>
        <div class="mr-error">
            <?php _e('شما به عنوان بیمار در سیستم ثبت نشده‌اید.', 'medical-records'); ?>
        </div>
    <?php else : 
        $medical_record = Medical_Records_DB::get_medical_record_by_customer($bookly_customer['id']);
    ?>
    
    <div id="mr-patient-info-card" class="mr-card">
        <h3><?php _e('اطلاعات بیمار', 'medical-records'); ?></h3>
        <p><strong><?php _e('نام:', 'medical-records'); ?></strong> <?php echo esc_html($bookly_customer['full_name']); ?></p>
        <p><strong><?php _e('تلفن:', 'medical-records'); ?></strong> <?php echo esc_html($bookly_customer['phone']); ?></p>
        <p><strong><?php _e('ایمیل:', 'medical-records'); ?></strong> <?php echo esc_html($bookly_customer['email']); ?></p>
    </div>
    
    <?php if ($medical_record) : ?>
        <div id="mr-medical-history-card" class="mr-card" style="margin-top: 20px;">
            <h3><?php _e('سوابق پزشکی', 'medical-records'); ?></h3>
            <p><strong><?php _e('گروه خونی:', 'medical-records'); ?></strong> <?php echo esc_html($medical_record['blood_group']); ?></p>
            <p><strong><?php _e('سن:', 'medical-records'); ?></strong> <?php echo esc_html($medical_record['age']); ?></p>
            <p><strong><?php _e('بیماری‌های خاص:', 'medical-records'); ?></strong> <?php echo nl2br(esc_html($medical_record['special_diseases'])); ?></p>
            <p><strong><?php _e('داروهای مصرفی:', 'medical-records'); ?></strong> <?php echo nl2br(esc_html($medical_record['current_medications'])); ?></p>
            
            <button class="button button-primary" id="mr-show-edit-history" style="margin-top: 15px;">
                <?php _e('ویرایش سوابق', 'medical-records'); ?>
            </button>
        </div>
        
        <div id="mr-edit-history-form" class="mr-card" style="display:none; margin-top: 20px;">
            <h3><?php _e('ثبت سوابق پزشکی', 'medical-records'); ?></h3>
            
            <div class="mr-form-row">
                <label><?php _e('گروه خونی:', 'medical-records'); ?></label>
                <select name="blood_group" class="mr-blood-group">
                    <option value=""><?php _e('انتخاب کنید', 'medical-records'); ?></option>
                    <option value="A+" <?php selected($medical_record['blood_group'], 'A+'); ?>>A+</option>
                    <option value="A-" <?php selected($medical_record['blood_group'], 'A-'); ?>>A-</option>
                    <option value="B+" <?php selected($medical_record['blood_group'], 'B+'); ?>>B+</option>
                    <option value="B-" <?php selected($medical_record['blood_group'], 'B-'); ?>>B-</option>
                    <option value="AB+" <?php selected($medical_record['blood_group'], 'AB+'); ?>>AB+</option>
                    <option value="AB-" <?php selected($medical_record['blood_group'], 'AB-'); ?>>AB-</option>
                    <option value="O+" <?php selected($medical_record['blood_group'], 'O+'); ?>>O+</option>
                    <option value="O-" <?php selected($medical_record['blood_group'], 'O-'); ?>>O-</option>
                </select>
            </div>
            
            <div class="mr-form-row">
                <label><?php _e('سن:', 'medical-records'); ?></label>
                <input type="number" name="age" class="regular-text" min="0" max="150" value="<?php echo esc_attr($medical_record['age']); ?>">
            </div>
            
            <div class="mr-form-row">
                <label><?php _e('بیماری‌های خاص:', 'medical-records'); ?></label>
                <div class="mr-checkbox-group">
                    <label><input type="checkbox" name="special_diseases[]" value="diabetes"> <?php _e('دیابت', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="hypertension"> <?php _e('فشار خون', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="heart_disease"> <?php _e('بیماری قلبی', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="asthma"> <?php _e('آسم', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="thyroid"> <?php _e('تیروئید', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="kidney"> <?php _e('بیماری کلیوی', 'medical-records'); ?></label>
                </div>
                <textarea name="other_diseases" class="large-text" rows="2" placeholder="<?php _e('سایر بیماری‌ها', 'medical-records'); ?>"></textarea>
            </div>
            
            <div class="mr-form-row">
                <label><?php _e('داروهای مصرفی:', 'medical-records'); ?></label>
                <div id="mr-patient-medications-container">
                    <div class="mr-medication-row">
                        <input type="text" name="medication_name[]" placeholder="<?php _e('نام دارو', 'medical-records'); ?>" class="regular-text">
                        <input type="text" name="medication_usage[]" placeholder="<?php _e('نحوه مصرف', 'medical-records'); ?>" class="regular-text">
                        <button class="button mr-remove-medication">×</button>
                    </div>
                </div>
                <button class="button" id="mr-add-patient-medication"><?php _e('+ افزودن دارو', 'medical-records'); ?></button>
            </div>
            
            <div class="mr-form-row">
                <label><?php _e('فایل‌های پزشکی:', 'medical-records'); ?></label>
                <div id="mr-patient-files-container">
                    <div class="mr-file-row">
                        <input type="text" name="file_title[]" placeholder="<?php _e('عنوان فایل', 'medical-records'); ?>" class="regular-text">
                        <input type="file" name="file_upload[]" class="mr-file-upload">
                        <button class="button mr-remove-file">×</button>
                    </div>
                </div>
                <button class="button" id="mr-add-patient-file"><?php _e('+ افزودن فایل', 'medical-records'); ?></button>
            </div>
            
            <div class="mr-form-actions">
                <button class="button button-primary" id="mr-submit-medical-history">
                    <?php _e('ثبت اطلاعات', 'medical-records'); ?>
                </button>
                <button class="button" id="mr-cancel-edit-history">
                    <?php _e('انصراف', 'medical-records'); ?>
                </button>
            </div>
        </div>
        
        <div class="mr-filters-section" style="margin-top: 20px;">
            <h3><?php _e('فیلتر ویزیت‌ها', 'medical-records'); ?></h3>
            <div class="mr-filter-row">
                <select id="mr-filter-clinic" class="mr-filter-select">
                    <option value=""><?php _e('همه کلینیک‌ها', 'medical-records'); ?></option>
                </select>
                
                <select id="mr-filter-doctor" class="mr-filter-select">
                    <option value=""><?php _e('همه پزشکان', 'medical-records'); ?></option>
                </select>
                
                <input type="text" id="mr-filter-date-from" class="mr-datepicker" placeholder="<?php _e('از تاریخ', 'medical-records'); ?>">
                <input type="text" id="mr-filter-date-to" class="mr-datepicker" placeholder="<?php _e('تا تاریخ', 'medical-records'); ?>">
                
                <button class="button" id="mr-apply-filters"><?php _e('اعمال فیلتر', 'medical-records'); ?></button>
            </div>
        </div>
        
        <div id="mr-visits-list" class="mr-visits-table" style="margin-top: 20px;">
            <h3><?php _e('لیست ویزیت‌ها', 'medical-records'); ?></h3>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th><?php _e('تاریخ ویزیت', 'medical-records'); ?></th>
                        <th><?php _e('پزشک', 'medical-records'); ?></th>
                        <th><?php _e('کلینیک', 'medical-records'); ?></th>
                        <th><?php _e('عملیات', 'medical-records'); ?></th>
                    </tr>
                </thead>
                <tbody id="mr-visits-tbody">
                </tbody>
            </table>
        </div>
        
        <div id="mr-visit-details-modal" class="mr-modal" style="display:none;">
            <div class="mr-modal-content">
                <span class="mr-close-modal">&times;</span>
                <h3><?php _e('جزئیات ویزیت', 'medical-records'); ?></h3>
                <div id="mr-visit-details-content"></div>
            </div>
        </div>
        
    <?php else : ?>
        <div class="mr-info" style="margin-top: 20px; padding: 20px; background: #f0f7ff; border-radius: 5px;">
            <p><?php _e('هنوز پرونده پزشکی برای شما ایجاد نشده است.', 'medical-records'); ?></p>
            <p><?php _e('برای ایجاد پرونده با پزشک یا مدیر سیستم تماس بگیرید.', 'medical-records'); ?></p>
        </div>
        
        <!-- Button to request medical record creation -->
        <div style="margin-top: 20px;">
            <button class="button button-primary" id="mr-request-record-btn">
                <?php _e('درخواست ایجاد پرونده', 'medical-records'); ?>
            </button>
        </div>
        
        <div id="mr-request-form" style="display:none; margin-top: 20px;" class="mr-card">
            <h3><?php _e('ثبت سوابق پزشکی اولیه', 'medical-records'); ?></h3>
            
            <div class="mr-form-row">
                <label><?php _e('گروه خونی:', 'medical-records'); ?></label>
                <select name="blood_group" class="mr-blood-group">
                    <option value=""><?php _e('انتخاب کنید', 'medical-records'); ?></option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                </select>
            </div>
            
            <div class="mr-form-row">
                <label><?php _e('سن:', 'medical-records'); ?></label>
                <input type="number" name="age" class="regular-text" min="0" max="150">
            </div>
            
            <div class="mr-form-row">
                <label><?php _e('بیماری‌های خاص:', 'medical-records'); ?></label>
                <div class="mr-checkbox-group">
                    <label><input type="checkbox" name="special_diseases[]" value="دیابت"> <?php _e('دیابت', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="فشار خون"> <?php _e('فشار خون', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="بیماری قلبی"> <?php _e('بیماری قلبی', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="آسم"> <?php _e('آسم', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="تیروئید"> <?php _e('تیروئید', 'medical-records'); ?></label>
                    <label><input type="checkbox" name="special_diseases[]" value="بیماری کلیوی"> <?php _e('بیماری کلیوی', 'medical-records'); ?></label>
                </div>
                <textarea name="other_diseases" class="large-text" rows="2" placeholder="<?php _e('سایر بیماری‌ها', 'medical-records'); ?>"></textarea>
            </div>
            
            <div class="mr-form-row">
                <label><?php _e('داروهای مصرفی:', 'medical-records'); ?></label>
                <div id="mr-patient-medications-container">
                    <div class="mr-medication-row">
                        <input type="text" name="medication_name[]" placeholder="<?php _e('نام دارو', 'medical-records'); ?>" class="regular-text">
                        <input type="text" name="medication_usage[]" placeholder="<?php _e('نحوه مصرف', 'medical-records'); ?>" class="regular-text">
                        <button class="button mr-remove-medication">×</button>
                    </div>
                </div>
                <button class="button" id="mr-add-patient-medication"><?php _e('+ افزودن دارو', 'medical-records'); ?></button>
            </div>
            
            <div class="mr-form-actions">
                <button class="button button-primary" id="mr-submit-medical-history">
                    <?php _e('ثبت اطلاعات', 'medical-records'); ?>
                </button>
            </div>
        </div>
    <?php endif; ?>
    
    <?php endif; ?>
</div>

<div id="mr-toast" class="mr-toast"></div>
