<div class="wrap">
    <h1><?php _e('لیست بیماران', 'medical-records'); ?></h1>
    
    <table class="wp-list-table widefat fixed striped" id="mr-patients-table">
        <thead>
            <tr>
                <th><?php _e('ID', 'medical-records'); ?></th>
                <th><?php _e('نام کامل', 'medical-records'); ?></th>
                <th><?php _e('تلفن', 'medical-records'); ?></th>
                <th><?php _e('عملیات', 'medical-records'); ?></th>
            </tr>
        </thead>
        <tbody>
            <?php 
            $patients = Medical_Records_DB::get_patients();
            if (empty($patients)) : 
            ?>
                <tr>
                    <td colspan="4"><?php _e('بیماری یافت نشد.', 'medical-records'); ?></td>
                </tr>
            <?php else : ?>
                <?php foreach ($patients as $patient) : 
                    $medical_record = Medical_Records_DB::get_medical_record_by_customer($patient['id']);
                ?>
                    <tr data-patient-id="<?php echo esc_attr($patient['id']); ?>">
                        <td><?php echo esc_html($patient['id']); ?></td>
                        <td><?php echo esc_html($patient['full_name']); ?></td>
                        <td><?php echo esc_html($patient['phone']); ?></td>
                        <td>
                            <?php if ($medical_record) : ?>
                                <button class="button button-small mr-view-record" data-record-id="<?php echo esc_attr($medical_record['id']); ?>">
                                    <?php _e('مشاهده پرونده', 'medical-records'); ?>
                                </button>
                                <button class="button button-small button-link-delete mr-delete-record" data-record-id="<?php echo esc_attr($medical_record['id']); ?>">
                                    <?php _e('حذف پرونده', 'medical-records'); ?>
                                </button>
                            <?php else : ?>
                                <button class="button button-small button-primary mr-create-record-btn">
                                    <?php _e('ایجاد پرونده', 'medical-records'); ?>
                                </button>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>
    
    <div id="mr-create-record-form" style="display:none; margin-top: 20px;">
        <h3><?php _e('ایجاد پرونده پزشکی', 'medical-records'); ?></h3>
        <div class="mr-form-container">
            <label><?php _e('انتخاب بیمار:', 'medical-records'); ?></label>
            <select class="mr-patient-select2" style="width: 300px;"></select>
            <br><br>
            <button class="button button-primary" id="mr-init-create-record">
                <?php _e('ایجاد پرونده', 'medical-records'); ?>
            </button>
        </div>
    </div>
    
    <div id="mr-full-create-form" style="display:none; margin-top: 20px; border-top: 2px solid #ccc; padding-top: 20px;">
        <h3><?php _e('تکمیل اطلاعات پرونده', 'medical-records'); ?></h3>
        <div class="mr-form-container">
            <div id="mr-selected-patient-info" style="background: #f9f9f9; padding: 15px; margin-bottom: 15px;"></div>
            
            <p>
                <label><?php _e('پزشک مسئول:', 'medical-records'); ?></label><br>
                <select name="doctor_id" class="mr-doctor-select" style="width: 300px;">
                    <option value=""><?php _e('انتخاب پزشک', 'medical-records'); ?></option>
                    <?php 
                    $doctors = Medical_Records_DB::get_doctors();
                    foreach ($doctors as $doctor) :
                    ?>
                        <option value="<?php echo esc_attr($doctor['id']); ?>"><?php echo esc_html($doctor['full_name']); ?></option>
                    <?php endforeach; ?>
                </select>
            </p>
            
            <p>
                <label><?php _e('گروه خونی:', 'medical-records'); ?></label><br>
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
            </p>
            
            <p>
                <label><?php _e('سن:', 'medical-records'); ?></label><br>
                <input type="number" name="age" class="regular-text" min="0" max="150">
            </p>
            
            <p>
                <label><?php _e('بیماری‌های خاص:', 'medical-records'); ?></label><br>
                <textarea name="special_diseases" class="large-text" rows="3"></textarea>
            </p>
            
            <p>
                <label><?php _e('داروهای مصرفی:', 'medical-records'); ?></label><br>
                <textarea name="current_medications" class="large-text" rows="3"></textarea>
            </p>
            
            <p>
                <button class="button button-primary" id="mr-submit-create-record">
                    <?php _e('تایید و ایجاد پرونده', 'medical-records'); ?>
                </button>
                <button class="button" id="mr-cancel-create-record">
                    <?php _e('بازگشت', 'medical-records'); ?>
                </button>
            </p>
        </div>
    </div>
    
    <div id="mr-view-record-container" style="display:none; margin-top: 20px;">
    </div>
</div>
