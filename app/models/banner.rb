class Banner < ActiveRecord::Base
  acts_as_taggable_on :categories

  default_scope :conditions => { :hide => false }, :order => 'position,id DESC'

  scope :unhide, :conditions => { :hide => false }, :order => 'position,id DESC'
  scope :published, where("publish = true AND (date_begin_at <= :time AND
                          (date_end_at is NULL OR date_end_at > :time))",
                          { :time => Time.now })

  scope :titles_or_texts_like, lambda { |str|
    where("LOWER(title) like :str OR LOWER(text) like :str", { :str => "%#{str.try(:downcase)}%"})}

  belongs_to :page, foreign_key: "page_id"
  belongs_to :repository, :foreign_key => "repository_id"
  belongs_to :user, :foreign_key => "user_id"
  belongs_to :site, :foreign_key => "site_id"

  validates_presence_of :title, :user_id, :date_begin_at

  validate :page_or_url

  def page_or_url
    if (url.blank? && page_id.blank?)
      errors.add(:banner, I18n.t("banner_need_a_destination"))
    end
  end
end
