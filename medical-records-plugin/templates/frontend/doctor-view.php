<div class="mr-doctor-container">
    <h2><?php _e('پرونده‌های پزشکی', 'medical-records'); ?></h2>
    
    <div id="mr-create-record-section">
        <button class="button button-primary" id="mr-show-create-form">
            <?php _e('ایجاد پرونده جدید', 'medical-records'); ?>
        </button>
        
        <div id="mr-create-form-wrapper" style="display:none; margin-top: 20px;">
            <div class="mr-card">
                <h3><?php _e('انتخاب بیمار', 'medical-records'); ?></h3>
                <select class="mr-patient-select2" style="width: 100%;"></select>
                <br><br>
                <button class="button button-primary" id="mr-init-create-record">
                    <?php _e('ایجاد پرونده', 'medical-records'); ?>
                </button>
            </div>
            
            <div id="mr-full-create-form" style="display:none; margin-top: 20px;">
                <hr style="margin: 20px 0;">
                <div class="mr-selected-patient-info" style="background: #f0f7ff; padding: 15px; border-radius: 5px; margin-bottom: 15px;"></div>
                
                <div class="mr-form-row">
                    <label><?php _e('پزشک مسئول:', 'medical-records'); ?></label>
                    <select name="doctor_id" class="mr-doctor-select" style="width: 100%;">
                        <option value=""><?php _e('انتخاب پزشک', 'medical-records'); ?></option>
                        <?php 
                        $doctors = Medical_Records_DB::get_doctors();
                        foreach ($doctors as $doctor) :
                        ?>
                            <option value="<?php echo esc_attr($doctor['id']); ?>"><?php echo esc_html($doctor['full_name']); ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <div class="mr-form-row">
                    <label><?php _e('گروه خونی:', 'medical-records'); ?></label>
                    <select name="blood_group" class="mr-blood-group">
                        <option value="">-</option>
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
                    <textarea name="special_diseases" class="large-text" rows="3"></textarea>
                </div>
                
                <div class="mr-form-row">
                    <label><?php _e('داروهای مصرفی:', 'medical-records'); ?></label>
                    <textarea name="current_medications" class="large-text" rows="3"></textarea>
                </div>
                
                <div class="mr-form-actions">
                    <button class="button button-primary" id="mr-submit-create-record">
                        <?php _e('تایید و ایجاد پرونده', 'medical-records'); ?>
                    </button>
                    <button class="button" id="mr-cancel-create-record">
                        <?php _e('بازگشت', 'medical-records'); ?>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <div id="mr-view-record-section" style="display:none; margin-top: 30px;">
        <button class="button mr-back-to-list" style="margin-bottom: 15px;">
            <span class="dashicons dashicons-arrow-left-alt2"></span>
            <?php _e('بازگشت', 'medical-records'); ?>
        </button>
        
        <div id="mr-patient-info-card" class="mr-card">
            <h3><?php _e('اطلاعات بیمار', 'medical-records'); ?></h3>
            <div id="mr-patient-details"></div>
        </div>
        
        <div id="mr-medical-history-card" class="mr-card" style="margin-top: 20px;">
            <h3><?php _e('سوابق پزشکی', 'medical-records'); ?></h3>
            <div id="mr-medical-history-details"></div>
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
        
        <div style="margin-top: 20px; text-align: left;">
            <button class="button button-primary" id="mr-show-visit-form">
                <?php _e('ثبت ویزیت', 'medical-records'); ?>
            </button>
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
        
        <div id="mr-visit-form-wrapper" style="display:none; margin-top: 20px;">
            <div class="mr-card">
                <h3><?php _e('ثبت ویزیت جدید', 'medical-records'); ?></h3>
                
                <div class="mr-form-row">
                    <label><?php _e('علت مراجعه:', 'medical-records'); ?></label>
                    <textarea name="complaint" class="large-text" rows="3"></textarea>
                </div>
                
                <div class="mr-form-row">
                    <label><?php _e('تشخیص:', 'medical-records'); ?></label>
                    <textarea name="diagnosis" class="large-text" rows="3"></textarea>
                </div>
                
                <div class="mr-form-row">
                    <label><?php _e('داروهای تجویزی:', 'medical-records'); ?></label>
                    <div id="mr-medications-container">
                        <div class="mr-medication-row">
                            <input type="text" name="medication_name[]" placeholder="<?php _e('نام دارو', 'medical-records'); ?>" class="regular-text">
                            <input type="text" name="medication_usage[]" placeholder="<?php _e('نحوه مصرف', 'medical-records'); ?>" class="regular-text">
                            <button class="button mr-remove-medication">×</button>
                        </div>
                    </div>
                    <button class="button" id="mr-add-medication"><?php _e('+ افزودن دارو', 'medical-records'); ?></button>
                </div>
                
                <div class="mr-form-row">
                    <label><?php _e('فایل‌های پیوست:', 'medical-records'); ?></label>
                    <div id="mr-files-container">
                        <div class="mr-file-row">
                            <input type="text" name="file_title[]" placeholder="<?php _e('عنوان فایل', 'medical-records'); ?>" class="regular-text">
                            <input type="file" name="file_upload[]" class="mr-file-upload">
                            <button class="button mr-remove-file">×</button>
                        </div>
                    </div>
                    <button class="button" id="mr-add-file"><?php _e('+ افزودن فایل', 'medical-records'); ?></button>
                </div>
                
                <div class="mr-form-actions">
                    <button class="button button-primary" id="mr-submit-visit">
                        <?php _e('ثبت ویزیت', 'medical-records'); ?>
                    </button>
                    <button class="button" id="mr-cancel-visit">
                        <?php _e('انصراف', 'medical-records'); ?>
                    </button>
                </div>
            </div>
        </div>
        
        <div id="mr-visit-details-modal" class="mr-modal" style="display:none;">
            <div class="mr-modal-content">
                <span class="mr-close-modal">&times;</span>
                <h3><?php _e('جزئیات ویزیت', 'medical-records'); ?></h3>
                <div id="mr-visit-details-content"></div>
            </div>
        </div>
    </div>
</div>

<div id="mr-toast" class="mr-toast"></div>
